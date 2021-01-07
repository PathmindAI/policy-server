from utils import get_model, save_file, get_preprocessor, get_output_mapper, get_num_actions
from config import OUTPUT_MAPPER_FILE, PREPROCESSOR_FILE, MODEL_FOLDER, USER, PASSWORD, DISCRETE_ACTIONS, TUPLE
import os
import tensorflow as tf
import numpy as np
from flask import send_file
import zipfile
import io
import pathlib

# dummy tensor creation, done once at start-up
is_training_tensor = tf.constant(False, dtype=tf.bool)
prev_reward_tensor = tf.constant([0], dtype=tf.float32)
prev_action_tensor = tf.constant([0], dtype=tf.int64)
seq_lens_tensor = tf.constant([0], dtype=tf.int32)
ACTION_KEY = None


def basic_auth(username: str, password: str, required_scopes=None):
    """Basic authentication endpoint as specified by Swagger.

    :param username: user name
    :param password: password
    :param required_scopes: optional scoping rules (unused, but we have to keep this required arg)
    :return:
    """
    if username == USER and password == PASSWORD:
        return {'admin': 'admin'}
    return None


def save_preprocessor(preprocessor_file):
    """ Save the uploaded preprocessor Python file.
    """
    return save_file(
        file_object=preprocessor_file,
        save_to=PREPROCESSOR_FILE, 
        allowed_extensions=["py"])


def save_output_mapper(output_mapper_file):
    """ Save the uploaded output mapper YAML file.
    """
    return save_file(
        file_object=output_mapper_file,
        save_to=OUTPUT_MAPPER_FILE, 
        allowed_extensions=["yaml", "yml"])


def save_model(model_file):
    """ Save the uploaded policy model file.
    """
    return save_file(
        file_object=model_file,
        save_to=os.path.join(MODEL_FOLDER, model_file.filename),
        allowed_extensions=["pth", "pt", "zip"],
        is_model=True)


def predict_deterministic(observation: dict):
    """Note: this is a hack, as we'd need the original 'env' used for training
    to restore the agent. Not in itself a problem, just less convenient compared
    to what we have now (don't need big JARs hanging around)."""
    if not DISCRETE_ACTIONS:
        return "Endpoint only available for discrete actions", 405
    if TUPLE:
        return "Endpoint only available for non-tuple scenarios"
    max_action = None
    max_prob = 0.0
    actions = {}
    while True:
        response = predict(observation)
        probability = response.get('probability')
        actions[response.get('action')] = probability
        if probability > max_prob:
            max_prob = probability
            max_action = response
        if max_prob > 1 - sum(actions.values()):
            return max_action


def distribution(observation: dict):
    if not DISCRETE_ACTIONS:
        return "Endpoint only available for discrete actions", 405
    if TUPLE:
        return "Endpoint only available for non-tuple scenarios"
    distro_dict = {}
    num_actions = get_num_actions()
    found_all_actions = False
    while not found_all_actions:
        response = predict(observation)
        distro_dict[response.get('meaning')] = response.get('probability')
        if len(distro_dict) is num_actions:
            found_all_actions = True
    return dict(sorted(distro_dict.items(), key=lambda x: x[0].lower()))


def predict(observation: dict):
    """ Predict the next action given an observation.

    :param observation: dictionary with keys corresponding to raw observations needed
        to build up the input tensor of the policy, by running it through the preprocessor.
    :return: JSON with "action" and "meaning".
    """
    model, model_type = get_model()
    if not model:
        return "No model available, use '/model' route to upload one.", 405
    preprocess = get_preprocessor()
    if not preprocess:
        return "No preprocessor available, use '/preprocessor' route to upload one", 405
    output_mapper = get_output_mapper()
    if not output_mapper and DISCRETE_ACTIONS:
        return "No output mapper available for discrete actions, use '/output_mapper' route to upload one", 405

    processed_list = preprocess(observation)
    processed = np.reshape(np.asarray(processed_list), (1, len(processed_list)))

    if model_type == "tensorflow":
        inputs = tf.convert_to_tensor(processed, dtype=tf.float32, name='observations')

        result = model(observations=inputs, is_training=is_training_tensor, seq_lens=seq_lens_tensor,
                    prev_action=prev_action_tensor, prev_reward=prev_reward_tensor)
        

        # keys: 'action_logp', 'actions_0', 'action_prob', 'vf_preds', 'action_dist_inputs'
        action_keys = [k for k in result.keys() if "actions_" in k]
        if not action_keys:
            return "Model has no 'actions' key", 405

        action_prob_tensor = result.get("action_prob").numpy()
        probability = float(action_prob_tensor[0])

        conversion_type = int if DISCRETE_ACTIONS else float

        if not TUPLE:
            action_tensor = result.get(action_keys[0])
            numpy_tensor = action_tensor.numpy()
            action = conversion_type(numpy_tensor[0])
            if DISCRETE_ACTIONS:
                return {"action": action, "meaning": output_mapper.get(action), "probability": probability}
            else:
                return {"action": action, "probability": probability}
        else:
            numpy_tensors = [result.get(k).numpy() for k in action_keys]
            actions = [conversion_type(x) for x in numpy_tensors]
            meanings = [output_mapper.get(action) for action in actions]
            if DISCRETE_ACTIONS:
                return {"actions": actions, "meanings": meanings, "probability": probability}
            else:
                return {"actions": actions, "probability": probability}

    else:
        raise ValueError("Only TensorFlow models supported at the moment.")


def clients():
    """build a zip file in-memory and send it to the client."""
    base_path = pathlib.Path('./clients')
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for root, dirs, files in os.walk(base_path):
            for file in files:
                z.write(os.path.join(root, file))
    data.seek(0)
    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='clients.zip'
    )
