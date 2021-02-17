import tensorflow as tf
import numpy as np
from typing import List
from pydantic import BaseModel, create_model
import config
from fluent import sender
from fastapi import HTTPException

logger = sender.FluentSender('policy_server', host='0.0.0.0', port=24224)


Observation = create_model(
    'Observation',
    **config.payload_data
)

class Experience(BaseModel):
    observation: Observation
    reward: float
    done: bool


class Action(BaseModel):
    actions: List[config.action_type]
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
        array = np.asarray(request.data)
        op = np.reshape(array, (1, array.size))
        tensors = tf.convert_to_tensor(op, dtype=tf.float32, name='observations')

        result = self.model(
            is_training=self.is_training_tensor, observations=tensors, prev_action=self.prev_action_tensor,
            prev_reward=self.prev_reward_tensor, seq_lens=self.seq_lens_tensor
        )

        action_keys = [k for k in result.keys() if "actions" in k]

        action_prob_tensor = result.get("action_prob").numpy()
        probability = float(action_prob_tensor[0])

        if not config.parameters.get("tuple"):
            action_tensor = result.get(action_keys[0])
            numpy_tensor = action_tensor.numpy()
            actions = [(config.action_type(numpy_tensor[0]))]
        else:
            numpy_tensors = [result.get(k).numpy() for k in action_keys]
            actions = [config.action_type(x) for x in numpy_tensors]

        global logger
        logger.emit('predict', {'observation': request.data, 'action': actions, 'probability': probability})

        return Action(actions=actions, probability=probability)


pm = PathmindPolicy()


def _predict(payload: Observation):
    class Dummy:
        data = None
    dummy = Dummy()
    dummy.data = payload
    return pm(dummy)


def _predict_deterministic(payload: Observation):
    """Note: this is a hack, as we'd need the original 'env' used for training
    to restore the agent. Not in itself a problem, just less convenient compared
    to what we have now (don't need big JARs hanging around)."""
    if not config.parameters.get("discrete"):
        raise HTTPException(status_code=405, detail="Endpoint only available for discrete actions")
    if config.parameters.get("tuple"):
        raise HTTPException(status_code=405, detail="Endpoint only available for non-tuple scenarios")

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
            return Action(actions=max_action, probability=max_prob)


def _distribution(payload: Observation):
    if not config.parameters.get("discrete"):
        raise HTTPException(status_code=405, detail="Endpoint only available for discrete actions")
    if config.parameters.get("tuple"):
        raise HTTPException(status_code=405, detail="Endpoint only available for non-tuple scenarios")
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
