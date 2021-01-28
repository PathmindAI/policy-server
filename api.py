import tensorflow as tf
import numpy as np
from typing import List
from pydantic import BaseModel, create_model
import oyaml as yaml
from collections import OrderedDict
from utils import unzip
from config import PATHMIND_POLICY, PATHMIND_SCHEMA


unzip(PATHMIND_POLICY)


with open(PATHMIND_SCHEMA, "r") as f:
    schema: OrderedDict = yaml.safe_load(f.read())

observations = schema.get("observations")
parameters = schema.get("parameters")
features = observations.keys()

payload_data = {k: (v.get("type"), ...) for k, v in observations.items()}

Payload = create_model(
    'Payload',
    **payload_data
)

action_type = int if parameters.get("discrete") else float


class Response(BaseModel):
    actions: List[action_type]
    probability: float


class PathmindPolicy:
    def __init__(self):
        self.is_training_tensor = tf.constant(False, dtype=tf.bool)
        self.prev_action_tensor = tf.constant([0], dtype=tf.int64)
        self.prev_reward_tensor = tf.constant([0], dtype=tf.float32)
        self.seq_lens_tensor = tf.constant([0], dtype=tf.int32)

        self.load_policy = tf.saved_model.load("models/")
        self.model = self.load_policy.signatures.get("serving_default")

    def __call__(self, request):
        data = request.data

        # TODO: potentially slow
        lists = [[getattr(data, obs)] if not isinstance(getattr(data, obs), List) else getattr(data, obs)
                 for obs in observations.keys()]
        import itertools
        merged = list(itertools.chain(*lists))
        array = np.asarray(merged)
        op = np.reshape(array, (1, array.size))
        tensors = tf.convert_to_tensor(op, dtype=tf.float32, name='observations')

        result = self.model(
            is_training=self.is_training_tensor, observations=tensors, prev_action=self.prev_action_tensor,
            prev_reward=self.prev_reward_tensor, seq_lens=self.seq_lens_tensor
        )

        action_keys = [k for k in result.keys() if "actions" in k]

        action_prob_tensor = result.get("action_prob").numpy()
        probability = float(action_prob_tensor[0])

        if not parameters.get("tuple"):
            action_tensor = result.get(action_keys[0])
            numpy_tensor = action_tensor.numpy()
            actions = [(action_type(numpy_tensor[0]))]
        else:
            numpy_tensors = [result.get(k).numpy() for k in action_keys]
            actions = [action_type(x) for x in numpy_tensors]

        return Response(actions=actions, probability=probability)


pm = PathmindPolicy()


def _predict(payload: Payload):
    class Dummy:
        data = None
    dummy = Dummy()
    dummy.data = payload
    return pm(dummy)


def _predict_deterministic(payload: Payload):
    """Note: this is a hack, as we'd need the original 'env' used for training
    to restore the agent. Not in itself a problem, just less convenient compared
    to what we have now (don't need big JARs hanging around)."""
    if not parameters.get("discrete"):
        return "Endpoint only available for discrete actions", 405
    if parameters.get("tuple"):
        return "Endpoint only available for non-tuple scenarios"

    max_action = None
    max_prob = 0.0
    actions = {}

    while True:
        response = _predict(payload)
        probability = response.probability
        actions[response.actions[0]] = probability
        if probability > max_prob:
            max_prob = probability
            max_action = response
        if max_prob > 1 - sum(actions.values()):
            return max_action


def _distribution(payload: Payload):
    if not parameters.get("discrete"):
        return "Endpoint only available for discrete actions", 405
    if parameters.get("tuple"):
        return "Endpoint only available for non-tuple scenarios"
    distro_dict = {}
    found_all_actions = False
    trials = 0
    while not found_all_actions:
        trials += 1
        response = _predict(payload)
        distro_dict[response.actions[0]] = response.probability
        if sum(distro_dict.values()) >= 0.99 or trials >= 100:
            found_all_actions = True
    return dict(sorted(distro_dict.items(), key=lambda x: str(x[0]).lower()))
