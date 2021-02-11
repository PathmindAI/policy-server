from mouse_env import MouseAndCheese
import requests

env = MouseAndCheese()

auth = ("admin", "admin")

for episode in range(100):
    obs = env.reset()
    reward = 0
    done = False
    while not done:
        obs_dict = {
            "mouse_row": obs[0],
            "mouse_col": obs[1],
            "mouse_row_dist": obs[2],
            "mouse_col_dist": obs[3],
        }
        payload = {
            "observation": obs_dict,
            "reward": reward,
            "done": done
        }

        response = requests.post("http://localhost:8000/collect_experience/", json=payload, auth=auth).json()
        action = response.get("actions")[0]
        obs, reward, done, info = env.step(action)
        if done:
            response = requests.post("http://localhost:8000/collect_experience/", json=payload, auth=auth).json()
            print(">>> Episode complete.")
