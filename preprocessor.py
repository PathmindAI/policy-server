import numpy as np


def preprocess(observation):
    arr = np.asarray([
        observation.get("id"),
        observation.get("coordinates")[0],
        observation.get("coordinates")[1],
        observation.get("has_up_neighbour"),
        observation.get("is_up_free"),
        observation.get("has_right_neighbour"),
        observation.get("is_right_free"),
        observation.get("has_down_neighbour"),
        observation.get("is_down_free"),
        observation.get("has_left_neighbour"),
        observation.get("is_left_free"),
        observation.get("has_core"),
        observation.get("target")[0],
        observation.get("target")[1],
    ])
    return np.reshape(arr, (1, 14))