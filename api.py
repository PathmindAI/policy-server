from utils import get_model, save_file, get_preprocessor, get_output_mapper
from config import OUTPUT_MAPPER_FILE, PREPROCESSOR_FILE, MODEL_FOLDER, USER, PASSWORD, BASE_PATH
import os
import tensorflow as tf
import numpy as np
from flask import send_from_directory, send_file
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
    if not output_mapper:
        return "No output mapper available, use '/output_mapper' route to upload one", 405

    processed_list = preprocess(observation)
    processed = np.reshape(np.asarray(processed_list), (1, len(processed_list)))

    if model_type == "tensorflow":
        inputs = tf.convert_to_tensor(processed, dtype=tf.float32, name='observations')

        result = model(observations=inputs, is_training=is_training_tensor, seq_lens=seq_lens_tensor,
                    prev_action=prev_action_tensor, prev_reward=prev_reward_tensor)
        
        global ACTION_KEY
        if not ACTION_KEY:
            # 'action_logp', 'actions_0', 'action_prob', 'vf_preds', 'action_dist_inputs'
            print(result.keys())
            action_keys = [k for k in result.keys() if "actions" in k]
            if not action_keys:
                return "Model has no 'actions' key", 405
            ACTION_KEY = action_keys[0]  # realistically just one

        action_tensor = result.get(ACTION_KEY)
        action = int(action_tensor.numpy()[0])

        action_prob_tensor = result.get("action_prob")
        action_prob = float(action_prob_tensor.numpy()[0])
        return {"action": action, "meaning": output_mapper.get(action), "probability": action_prob}
    else:
        return {"action": 0, "meaning": output_mapper.get(0), "probability": 1.0}


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
