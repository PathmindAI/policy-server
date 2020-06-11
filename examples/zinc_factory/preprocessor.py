def preprocess(obs):
    return [
        obs.get("hour") / 24,
        obs.get("day") / 365,
        obs.get("month") / 12,
        obs.get("30_minute_cost") / 1000,
        obs.get("price") / 40,
        obs.get("total_cost") / 1000000,
    ]
