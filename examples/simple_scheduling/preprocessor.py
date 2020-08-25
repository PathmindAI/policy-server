def preprocess(obs):
    return [
        obs.get("total_products_processed"),
        obs.get("machine1_seized"),
        obs.get("machine2_seized"),
        obs.get("seizeDelayStage1_queue"),
        obs.get("seizeDelayStage2_queue"),
        obs.get("seizeDelayStage3_queue"),
    ]
