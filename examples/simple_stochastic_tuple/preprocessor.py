def preprocess(obs):
    result = [0, 0, 0]
    result[obs.get("state")] = 1
    return result
