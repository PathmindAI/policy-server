"""Basic configuration for the application."""
import os


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
