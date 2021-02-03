import ray
from ray import serve
from fastapi import FastAPI
from fastapi.responses import FileResponse
import shutil
import itertools

import config
from api import Action, Observation
from api import _predict_deterministic, _distribution, _predict
from typing import List
from utils import unzip


SERVE_HANDLE = None
app = FastAPI()

unzip(config.PATHMIND_POLICY)


if config.USE_RAY:
    @app.on_event("startup")
    async def startup_event():

        ray.init(_metrics_export_port=8080)  # Initialize new ray instance
        client = serve.start(http_host=None)

        backend_config = serve.BackendConfig(num_replicas=4)

        from api import PathmindPolicy
        client.create_backend("pathmind_policy", PathmindPolicy, config=backend_config)
        client.create_endpoint("predict", backend="pathmind_policy")

        global SERVE_HANDLE
        SERVE_HANDLE = client.get_handle("predict")


@app.post("/predict/", response_model=Action)
async def predict(payload: Observation):
    if config.USE_RAY:

        lists = [[getattr(payload, obs)] if not isinstance(getattr(payload, obs), List) else getattr(payload, obs)
                 for obs in config.observations.keys()]
        merged = list(itertools.chain(*lists))
        # Note that ray can't pickle the pydantic "Observation" model, so we need to convert it here.
        return await SERVE_HANDLE.remote(merged)
    else:
        return _predict(payload)


@app.get("/clients")
async def clients():
    shutil.make_archive('clients', 'zip', './clients')
    return FileResponse(path='clients.zip', filename='clients.zip')


@app.post("/predict_deterministic/", response_model=Action)
async def predict_deterministic(payload: Observation):
    return _predict_deterministic(payload)


@app.post("/distribution/")
async def distribution(payload: Observation):
    return _distribution(payload)
