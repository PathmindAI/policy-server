import ray
from ray import serve

from fastapi import FastAPI

app = FastAPI()

SERVE_HANDLE = None

# TODO
