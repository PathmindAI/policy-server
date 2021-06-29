from fastapi.testclient import TestClient

from app import app
from generate import CLI

# Set up server
CLI.copy_server_files("examples/mouse_and_cheese")
client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "ok"


payload = {
    "mouse_row": 1,
    "mouse_col": 1,
    "mouse_row_distance": 1,
    "mouse_col_distance": 1,
    "cheese_row": 1,
    "cheese_col": 1,
}


def test_predict():
    response = client.post("http://localhost:8000/predict/", json=payload)
    assert response.status_code == 403
    response = client.post(
        "http://localhost:8000/predict/",
        json={"bad_payload": 1},
        headers={"access-token": "1234567asdfgh"},
    )
    print(f"status code: {response.status_code}")
    assert response.status_code == 422
    response = client.post(
        "http://localhost:8000/predict/",
        json=payload,
        headers={"access-token": "1234567asdfgh"},
    )
    print(f"status code: {response.status_code}")
    assert response.status_code == 200
    # assert len(response.json()["actions"]) == 1
    # assert response.json()["probability"] >= 0
    assert response.json()


# def test_predict(server):
# get predictions
# assert client code generated
# assert docs url running
#    predict()


# res = requests.get("http://localhost:8000/openapi.json")

# with open("../openapi.json", "w") as f:
#    f.write(res.content.decode("utf-8"))
