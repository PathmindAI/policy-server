"""Basic configuration for the application."""
import os

# Prediction type configuration
TUPLE = os.environ.get("TUPLE") if os.environ.get("TUPLE") else False
DISCRETE_ACTIONS = os.environ.get("DISCRETE_ACTIONS") if os.environ.get("DISCRETE_ACTIONS") else True


def base_path(local_file):
    """Join a local file with the BASE_PATH.
    :param local_file: relative path to file on your system.
    :return: joined path
    """
    return os.path.join(BASE_PATH, local_file)


# If you put BASE_PATH on your PATH we use that, otherwise the current working directory.
BASE_PATH = os.environ.get('BASE_PATH', os.path.expanduser("."))

# Naming conventions are fixed, as we can control names on upload.
MODEL_FOLDER = base_path("models")
PREPROCESSOR_FILE = base_path("preprocessor.py")
OUTPUT_MAPPER_FILE = base_path("output_mapper.yaml")
TF_MODEL_PATH = base_path("models/")
PY_TORCH_MODEL_PATH = base_path("models/model.pt")
SCHEMA_FILE = base_path("schema.yaml")
SWAGGER_TEMPLATE = base_path("swagger.template.yaml")
SWAGGER_FILE = base_path("swagger.yaml")

# Authentication
USER = "foo"
PASSWORD = "bar"

# API Versioning
API_PREFIX = "/api"
API_VERSION = "0.1"

# Web server configuration
USE_SSL = False
ADHOC_SSL = True
USE_TORNADO = False
DEBUG = os.environ.get("DEBUG", False)
USE_DOCKER = os.environ.get("USE_DOCKER", False)
HOST = "0.0.0.0" if USE_DOCKER else "localhost"
if os.environ.get("HOST"):
    HOST = os.environ.get("HOST")
PORT = os.environ.get("PORT", 8080)


def get_server_arguments():
    """Get arguments for starting the web server with the
    right configuration.

    :return:
    """
    kwargs = {}
    if USE_SSL:
        if ADHOC_SSL:
            context = "adhoc"
        else:
            # Note this assumes you created a cert/key pair in the `keys` folder.
            context = ('keys/cert.pem', 'keys/key.pem')
        kwargs['ssl_context'] = context
    if USE_TORNADO:
        kwargs['server'] = 'tornado'
    kwargs['host'] = HOST
    kwargs['port'] = PORT

    return kwargs


discrete_action = """definitions:
  Prediction:
    type: "object"
    properties:
      action:
        type: "integer"
        format: "int32"
      meaning:
        type: "string"
      probability:
        type: "number"
        format: "float"
    example:
      meaning: "meaning"
      action: 0
      probability: 0.96
"""

continuous_action = """definitions:
  Prediction:
    type: "object"
    properties:
      action:
        type: "number"
        format: "float"
      meaning:
        type: "string"
      probability:
        type: "number"
        format: "float"
    example:
      action: 1.0
      probability: 0.96
"""

tuple_continuous = """definitions:
  Prediction:
    type: "object"
    properties:
      actions:
        type: "array"
        items:
          type: "number"
          format: "float"
      probabilities:
        type: "array"
        items:
          type: "number"
    example:
      actions:
        - 0.5
        - 2.4
      probabilities:
        - 0.4
        - 0.6
"""

tuple_discrete = """definitions:
  Prediction:
    type: "object"
    properties:
      actions:
        type: "array"
        items:
          type: "integer"
          format: "int32"
      probabilities:
        type: "array"
        items:
          type: "number"
    example:
      actions:
        - 1
        - 2
      probabilities:
        - 0.4
        - 0.6
"""

def get_prediction_schema():
    if TUPLE and DISCRETE_ACTIONS:
        return tuple_discrete
    elif TUPLE and not DISCRETE_ACTIONS:
        return tuple_continuous
    if not TUPLE and DISCRETE_ACTIONS:
        return discrete_action
    else:
        return continuous_action
