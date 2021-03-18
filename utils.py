from config import *
import zipfile
import tensorflow as tf


def safe_remove(file_name):
    """Pythonic remove-if-exists."""
    try:
        os.remove(file_name)
    except OSError:
        pass


def get_extension(local_file: str) -> str:
    """Extract the file extension of a file."""
    return local_file.rsplit(".", 1)[1].lower()


def load_model():
    """Load a model from file into memory for inference."""
    tf_trackable = tf.saved_model.load(TF_MODEL_PATH)
    model = tf_trackable.signatures.get("serving_default")
    model_type = "tensorflow"
    return model, model_type


def unzip(local_file):
    """Unzip a file if it has a zip extension, otherwise leave as is."""
    extension = get_extension(local_file)
    if extension == "zip":
        with zipfile.ZipFile(local_file, 'r') as zip_ref:
            zip_ref.extractall(MODEL_FOLDER)
    print(">>> Successfully unzipped model.")
