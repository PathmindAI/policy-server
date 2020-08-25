def preprocess(obs):
    res = []
    for i in range(1, 7):
        pos = obs.get(f"table_{i}_node")
        one_hot_table = [0 for _ in range(33)]
        one_hot_table[pos] = 1
        res += one_hot_table
    for i in range(1, 7):
        pos = obs.get(f"table_{i}_target_node")
        one_hot_target = [0 for _ in range(33)]
        if pos >= 0:
            one_hot_target[pos] = 1
        res += one_hot_target

    return res
