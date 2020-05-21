import numpy as np


def preprocess(observation):
    arr = np.asarray([
        observation.get("mouse_row") / 5.0,
        observation.get("mouse_col") / 5.0,
        abs(4 - observation.get("mouse_row"))/ 5.0,
        abs(4 - observation.get("mouse_col"))/ 5.0,
    ])
    return np.reshape(arr, (1, 4))