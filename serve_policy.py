from ray import serve
# import ray
import tensorflow as tf

import numpy as np
import requests
import zipfile
from fastapi import FastAPI

from typing import List


PATHMIND_POLICY = "rail_policy.zip"
with zipfile.ZipFile(PATHMIND_POLICY, 'r') as zip_ref:
    TRAINED_MODEL_PATH = "MODEL_FOLDER"


app = FastAPI()

SERVE_HANDLE = None


@app.on_event("startup")  # Code to be run when the server starts.
async def startup_event():

    class PathmindPolicy:
        def __init__(self, model_path):
            self.is_training_tensor = tf.constant(False, dtype=tf.bool)
            self.prev_action_tensor = tf.constant([0], dtype=tf.int64)
            self.prev_reward_tensor = tf.constant([0], dtype=tf.float32)
            self.seq_lens_tensor = tf.constant([0], dtype=tf.int32)

            self.load_policy = tf.saved_model.load(model_path)
            self.model = self.load_policy.signatures.get("serving_default")

        def __call__(self, array):
            array = np.asarray(array)
            op = np.reshape(array, (1, array.size))
            result = self.model(
                is_training=self.is_training_tensor, observations=tensors, prev_action=self.prev_action_tensor,
                prev_reward=self.prev_reward_tensor, seq_lens=self.seq_lens_tensor
            )

            action_keys = [k for k in result.keys() if "actions_" in k]

            action_prob_tensor = result.get("action_prob").numpy()
            probability = float(action_prob_tensor[0])
            action_tensor = result.get(action_keys[0])
            action = action_tensor.numpy()

            return {"action": action.tolist(), "probability": probability}

    # Set up a backend with the desired number of replicas.
    import ray
    ray.init(address='auto')
    # ray.init(address="auto")  # Connect to the running Ray cluster.

    # backend_config = serve.BackendConfig(num_replicas=8)
    client = serve.start()
    client.create_backend("tf_model", PathmindPolicy, TRAINED_MODEL_PATH)
    client.create_endpoint("predict", backend="tf_model")

    # Get a handle to our Ray Serve endpoint so we can query it in Python.
    global SERVE_HANDLE
    SERVE_HANDLE = client.get_handle("predict")


@app.post("/predict")
async def predict(array: List):
    return await SERVE_HANDLE.remote(array)
