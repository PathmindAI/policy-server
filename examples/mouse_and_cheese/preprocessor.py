def preprocess(obs):
    return [
        obs.get("mouse_row") / 5.0,
        obs.get("mouse_col") / 5.0,
        abs(4 - obs.get("mouse_row")) / 5.0,
        abs(4 - obs.get("mouse_col")) / 5.0,
    ]
