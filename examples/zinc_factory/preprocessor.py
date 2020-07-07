def preprocess(obs):
    return [
        obs.get("minute"),
        obs.get("hour"),
        obs.get("day"),
        obs.get("month"),
        obs.get("price"),
    ]
