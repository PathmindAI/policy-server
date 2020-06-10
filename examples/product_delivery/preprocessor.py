def preprocess(obs):
    return [
        obs.get("manufacturing_center_0_stock") / 1000,
        obs.get("manufacturing_center_1_stock") / 1000,
        obs.get("manufacturing_center_2_stock") / 1000,
        obs.get("manufacturing_center_0_total_vehicles") / 3,
        obs.get("manufacturing_center_1_total_vehicles") / 3,
        obs.get("manufacturing_center_2_total_vehicles") / 3,
        obs.get("manufacturing_center_0_distance") / 1000000,
        obs.get("manufacturing_center_1_distance") / 1000000,
        obs.get("manufacturing_center_2_distance") / 1000000,
        obs.get("manufacturing_center_0_available_vehicles") / 3,
        obs.get("manufacturing_center_1_available_vehicles") / 3,
        obs.get("manufacturing_center_2_available_vehicles") / 3,
        obs.get("current_order_amount") / 1000,
    ]
