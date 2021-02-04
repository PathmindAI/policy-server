"""Basic configuration for the application."""
import os
import oyaml as yaml
from collections import OrderedDict

USE_RAY = True


def base_path(local_file):
    """Join a local file with the BASE_PATH.
    :param local_file: relative path to file on your system.
    :return: joined path
    """
    return os.path.join(BASE_PATH, local_file)


# If you put BASE_PATH on your PATH we use that, otherwise the current working directory.
BASE_PATH = os.environ.get('BASE_PATH', os.path.expanduser("."))

PATHMIND_POLICY = base_path("saved_model.zip")
PATHMIND_SCHEMA = base_path("schema.yaml")

# Naming conventions are fixed, as we can control names on upload.
MODEL_FOLDER = base_path("models")
TF_MODEL_PATH = base_path("models/")
SWAGGER_FILE = "http://localhost:8000/openapi.json"
LOCAL_SWAGGER = base_path("openapi.json")
CLIENTS_ZIP = base_path("clients.zip")


USER_NAME = "admin"
PASSWORD = "admin"


with open(PATHMIND_SCHEMA, "r") as f:
    schema: OrderedDict = yaml.safe_load(f.read())

observations = schema.get("observations")
parameters = schema.get("parameters")
features = observations.keys()
action_type = int if parameters.get("discrete") else float

payload_data = {k: (v.get("type"), ...) for k, v in observations.items()}


