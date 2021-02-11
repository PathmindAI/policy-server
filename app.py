import ray
from ray import serve
import shutil
import itertools
import json
import yaml

import config
from api import Action, Observation, Experience
from api import _predict_deterministic, _distribution, _predict
from typing import List
from utils import unzip
from generate import CLI

import secrets
from fastapi.responses import FileResponse
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.utils import get_openapi

from ray.rllib.evaluation.sample_batch_builder import SampleBatchBuilder
from ray.rllib.offline.json_writer import JsonWriter
from offline import EpisodeCache

cache = EpisodeCache()
batch_builder = SampleBatchBuilder()  # or MultiAgentSampleBatchBuilder
writer = JsonWriter(config.EXPERIENCE_LOCATION)


tags_metadata = [
    {
        "name": "Predictions",
        "description": "Get actions for your next observations.",
    },
    {
        "name": "Clients",
        "description": "Get libraries in several programming languages to connect with this server.",
    },
    {
        "name": "Health",
        "description": "Basic health checks.",
    },
]


SERVE_HANDLE = None

app = FastAPI()

security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, config.USER_NAME)
    correct_password = secrets.compare_digest(credentials.password, config.PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


unzip(config.PATHMIND_POLICY)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Pathmind Policy Server",
        description="Serve your policies in production",
        version="1.0.0",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://i2.wp.com/pathmind.com/wp-content/uploads/2020/07/pathmind-logo-blue.png?w=1176&ssl=1"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


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


@app.post("/predict/", response_model=Action, tags=["Predictions"])
async def predict(payload: Observation, logged_in: bool = Depends(verify_credentials)):
    if config.USE_RAY:

        lists = [[getattr(payload, obs)] if not isinstance(getattr(payload, obs), List) else getattr(payload, obs)
                 for obs in config.observations.keys()]
        observations = list(itertools.chain(*lists))
        # Note that ray can't pickle the pydantic "Observation" model, so we need to convert it here.
        return await SERVE_HANDLE.remote(observations)
    else:
        return _predict(payload)


@app.post("/collect_experience/", response_model=Action, tags=["Predictions"])
async def collect_experience(payload: Experience, logged_in: bool = Depends(verify_credentials)):

    global cache
    global batch_builder

    observation = payload.observation
    rew = payload.reward
    done = payload.done

    lists = [[getattr(observation, obs)] if not isinstance(getattr(observation, obs), List) else getattr(observation, obs)
             for obs in config.observations.keys()]
    obs = list(itertools.chain(*lists))
    action = _predict(obs)

    if cache.is_empty():
        cache.store(t=0, prev_obs=obs, prev_action=action.actions, prev_reward=rew)

    batch_builder.add_values(
        agent_index=0,
        actions=action.actions,
        action_prob=action.probability,
        t=cache.t,
        eps_id=cache.episode,

        prev_actions=cache.prev_action,
        prev_rewards=cache.prev_reward,
        obs=cache.prev_obs,

        # sent from environment
        new_obs=obs,
        dones=done,
        infos=None,
        rewards=rew,
    )
    cache.store(t=cache.t+1, prev_obs=obs, prev_action=action.actions, prev_reward=rew)

    if done:
        print(">>> Writing offline batch")
        writer.write(batch_builder.build_and_reset())
        cache.reset()

    return action


@app.get("/clients", tags=["Clients"])
async def clients(logged_in: bool = Depends(verify_credentials)):
    shutil.make_archive('clients', 'zip', './clients')
    return FileResponse(path='clients.zip', filename='clients.zip')


@app.get("/schema", tags=["Clients"])
async def server_schema(logged_in: bool = Depends(verify_credentials)):
    with open(config.PATHMIND_SCHEMA, 'r') as schema_file:
        schema_str = schema_file.read()
    schema = yaml.safe_load(schema_str)
    return schema


@app.post("/predict_deterministic/", response_model=Action, tags=["Predictions"])
async def predict_deterministic(payload: Observation, logged_in: bool = Depends(verify_credentials)):
    return _predict_deterministic(payload)


@app.post("/distribution/", tags=["Predictions"])
async def distribution(payload: Observation, logged_in: bool = Depends(verify_credentials)):
    return _distribution(payload)


@app.get("/", tags=["Health"])
async def health_check():
    return "ok"


app.openapi = custom_openapi

# Write the swagger file locally
with open(config.LOCAL_SWAGGER, 'w') as f:
    f.write(json.dumps(app.openapi()))

# Generate all clients on startup
CLI.clients()