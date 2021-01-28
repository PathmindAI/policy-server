import ray
from ray import serve
from fastapi import FastAPI
from fastapi.responses import FileResponse
import shutil

import config
from api import Response, Payload
from api import _predict_deterministic, _distribution, _predict


SERVE_HANDLE = None
app = FastAPI()

if config.USE_RAY:
    @app.on_event("startup")
    async def startup_event():
        from api import PathmindPolicy

        ray.init(_metrics_export_port=8080)  # Initialize new ray instance
        client = serve.start(http_host=None)

        backend_config = serve.BackendConfig(num_replicas=4)
        client.create_backend("pathmind_policy", PathmindPolicy, config=backend_config)
        client.create_endpoint("predict", backend="pathmind_policy")

        global SERVE_HANDLE
        SERVE_HANDLE = client.get_handle("predict")


@app.post("/predict/", response_model=Response)
async def predict(payload: Payload):
    if config.USE_RAY:
        return await SERVE_HANDLE.remote(payload)
    else:
        return _predict(payload)


@app.get("/clients")
async def clients():
    shutil.make_archive('clients', 'zip', './clients')
    return FileResponse(path='clients.zip', filename='clients.zip')


@app.post("/predict_deterministic/", response_model=Response)
async def predict_deterministic(payload: Payload):
    return _predict_deterministic(payload)


@app.post("/distribution/")
async def predict_deterministic(payload: Payload):
    return _distribution(payload)
