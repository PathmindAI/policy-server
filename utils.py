import os
import yaml
import zipfile
from config import *
import tensorflow as tf


MODEL = None
MODEL_TYPE = None
OUTPUT_MAPPER = None

def get_model():
    global MODEL, MODEL_TYPE
    if not MODEL:
        MODEL, MODEL_TYPE = load_model()
    return MODEL, MODEL_TYPE


def get_preprocessor():
    if not os.path.exists(PREPROCESSOR_FILE):
        return None
    else:
        from preprocessor import preprocess
        return preprocess


def get_output_mapper():
    global OUTPUT_MAPPER
    if OUTPUT_MAPPER:
        return OUTPUT_MAPPER
    if not os.path.exists(OUTPUT_MAPPER_FILE):
        return None
    with open(OUTPUT_MAPPER_FILE, 'r') as stream:
        try:
            OUTPUT_MAPPER = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc
    return OUTPUT_MAPPER


def save_file(filename, save_to, allowed_extensions, is_model=False):
    if os.path.exists(save_to):
        os.remove(save_to)
    extension = get_extension(filename.filename)
    if extension in allowed_extensions:
        filename.save(save_to)
        if is_model:
            unzip(save_to)
            global MODEL, MODEL_TYPE
            MODEL, MODEL_TYPE = load_model()
        return f"{filename.filename} successfully uploaded!", 200
    else:
        return f"Uploading {filename} unsupported, allowed file extensions: {allowed_extensions}", 405


def get_extension(local_file):
    return local_file.rsplit(".", 1)[1].lower()


def load_model():
    if os.path.exists(TF_MODEL_PATH):
        tf_trackable = tf.saved_model.load(TF_MODEL_PATH)
        model = tf_trackable.signatures.get("serving_default")
        model_type = "tensorflow"
    else:
        # lazy load pytorch, as we don't use it right now
        # import torch
        # model = torch.load(PYTORCH_MODEL_PATH)
        # model_type = "torch"
        model, model_type = None, None
    return model, model_type


def unzip(local_file):
    extension = get_extension(local_file)
    if extension == "zip":
        with zipfile.ZipFile(local_file, 'r') as zip_ref:
            zip_ref.extractall(MODEL_FOLDER)