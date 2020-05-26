def preprocess(obs):
    return [
        obs.get("id"),
        obs.get("coordinates")[0],
        obs.get("coordinates")[1],
        obs.get("has_up_neighbour"),
        obs.get("is_up_free"),
        obs.get("has_right_neighbour"),
        obs.get("is_right_free"),
        obs.get("has_down_neighbour"),
        obs.get("is_down_free"),
        obs.get("has_left_neighbour"),
        obs.get("is_left_free"),
        obs.get("has_core"),
        obs.get("target")[0],
        obs.get("target")[1],
    ]
