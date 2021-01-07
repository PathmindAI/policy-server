from config import *

import yaml
import zipfile
import tensorflow as tf
from typing import List, Optional

# We set a few global variables here for the running app to access.
MODEL = None
MODEL_TYPE = None
OUTPUT_MAPPER = None


def safe_remove(file_name):
    """Pythonic remove-if-exists."""
    try:
        os.remove(file_name)
    except OSError:
        pass

def get_model():
    """Return model and type, caches the result."""
    global MODEL, MODEL_TYPE
    if not MODEL:
        MODEL, MODEL_TYPE = load_model()
    return MODEL, MODEL_TYPE


def get_preprocessor():
    """Load the preprocessor from file, if it exists."""
    if not os.path.exists(PREPROCESSOR_FILE):
        return None

    from preprocessor import preprocess
    return preprocess


def get_output_mapper() -> Optional[dict]:
    """Load the output mapping. Caches the result."""
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


def get_num_actions() -> Optional[int]:
    mapper: Optional[dict] = get_output_mapper()
    return len(mapper) if mapper else None


def save_file(file_object, save_to: str, allowed_extensions: List[str], is_model: bool = False):
    """ Save a file coming in through a multipart upload request.

    :param file_object: File upload object
    :param save_to: local path to save the uploaded file to.
    :param allowed_extensions: List of allowed file extensions.
    :param is_model: if the uploaded file is a model, try to unzip and load it.
    :return: HTTP response acknowledging the upload.
    """
    safe_remove(save_to)
    extension = get_extension(file_object.filename)
    if extension in allowed_extensions:
        file_object.save(save_to)
        if is_model:
            unzip(save_to)
            global MODEL, MODEL_TYPE
            MODEL, MODEL_TYPE = load_model()
        return f"{file_object.filename} successfully uploaded!", 200
    else:
        return f"Uploading {file_object} unsupported, allowed file extensions: {allowed_extensions}", 405


def get_extension(local_file: str) -> str:
    """Extract the file extension of a file."""
    return local_file.rsplit(".", 1)[1].lower()


def load_model():
    """Load a model from file into memory for inference."""
    if os.path.exists(TF_MODEL_PATH):
        tf_trackable = tf.saved_model.load(TF_MODEL_PATH)
        model = tf_trackable.signatures.get("serving_default")
        model_type = "tensorflow"
    else:
        # TODO support this.
        # lazy-load pytorch
        # import torch
        # model = torch.load(PYTORCH_MODEL_PATH)
        # model_type = "torch"
        model, model_type = None, None
    return model, model_type


def unzip(local_file):
    """Unzip a file if it has a zip extension, otherwise leave as is."""
    extension = get_extension(local_file)
    if extension == "zip":
        with zipfile.ZipFile(local_file, 'r') as zip_ref:
            # TODO: flatten intermediate folders.
            zip_ref.extractall(MODEL_FOLDER)
    print(">>> Successfully unzipped model.")
