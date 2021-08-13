import requests
import json

payload = {
    "mouse_row": 1,
    "mouse_col": 1,
    "mouse_row_dist": 1,
    "mouse_col_dist": 1,
}


def predict():
    res = requests.post("http://localhost:8000/predict", verify=False, json=payload)
    print(res.json())
    return res


predict()


res = requests.get("http://localhost:8000/openapi.json")

with open("../openapi.json", "w") as f:
    f.write(res.content.decode("utf-8"))
