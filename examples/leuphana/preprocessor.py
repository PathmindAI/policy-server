def preprocess(obs):
    return [
        obs.get("RacerGreen"),
        obs.get("RacerGray"),
        obs.get("ExotGreen"),
        obs.get("OrdersRacerGreen") ,
        obs.get("OrdersRacerGray") ,
        obs.get("OrdersExotGreen") ,
        obs.get("selectedProduct") ,
    ]
