import os


def base_path(local_file):
    return os.path.join(BASE_PATH, local_file)

if os.environ.get('BASE_PATH'):
    BASE_PATH = os.environ.get('BASE_PATH')
else:
    BASE_PATH = "."

MODEL_FOLDER = base_path("models")
PREPROCESSOR_FILE = base_path("preprocessor.py")
OUTPUT_MAPPER_FILE = base_path("output_mapper.yaml")
TF_MODEL_PATH = base_path("models/")
PYTORCH_MODEL_PATH = base_path("models/model.pt")
