from utils import get_model, save_file, get_preprocessor, get_output_mapper
from config import OUTPUT_MAPPER_FILE, PREPROCESSOR_FILE, MODEL_FOLDER
import os
import tensorflow as tf

# dummy tensor creation, do this once at the beginning
is_training_tensor = tf.constant(False, dtype=tf.bool)
prev_reward_tensor = tf.constant([0], dtype=tf.float32)
prev_action_tensor = tf.constant([0], dtype=tf.int64)
seq_lens_tensor = tf.constant([0], dtype=tf.int32)
ACTION_KEY = None


def basic_auth(username, password, required_scopes=None):
    if username == 'foo' and password == 'bar':
        return {'admin': 'admin'}

    return None


def save_preprocessor(preprocessor_file):
    return save_file(
        filename=preprocessor_file, 
        save_to=PREPROCESSOR_FILE, 
        allowed_extensions=["py"])


def save_output_mapper(output_mapper_file):
    return save_file(
        filename=output_mapper_file, 
        save_to=OUTPUT_MAPPER_FILE, 
        allowed_extensions=["yaml", "yml"])


def save_model(model_file):
    return save_file(
        filename=model_file, 
        save_to=os.path.join(MODEL_FOLDER, model_file.filename),
        allowed_extensions=["pth", "pt", "zip"],
        is_model=True)


def predict(observation):
    model, model_type = get_model()
    if not model:
        return "No model available, use '/model' route to upload one.", 405
    preprocess = get_preprocessor()
    if not preprocess:
        return "No preprocessor available, use '/preprocessor' route to upload one", 405
    output_mapper = get_output_mapper()
    if not output_mapper:
        return "No output mapper available, use '/output_mapper' route to upload one", 405

    processed = preprocess(observation)
    if model_type == "tensorflow":
        inputs = tf.convert_to_tensor(processed, dtype=tf.float32, name='observations')

        result = model(observations=inputs, is_training=is_training_tensor, seq_lens=seq_lens_tensor,
                    prev_action=prev_action_tensor, prev_reward=prev_reward_tensor)
        
        global ACTION_KEY
        if not ACTION_KEY:
            action_keys = [k for k in result.keys() if "actions" in k]
            if not action_keys:
                return "Model has no 'actions' key", 405
            ACTION_KEY = action_keys[0]  # realistically just one

        action_tensor = result.get(ACTION_KEY)
        action = int(action_tensor.numpy()[0])
        return {"action": action, "meaning": output_mapper.get(action)}
    else:
        return {"action": 0, "meaning": output_mapper.get(0)}


def clients():
    # TODO
    pass