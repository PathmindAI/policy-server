from multiprocessing import Process

import pytest
import requests
import uvicorn
from fastapi import FastAPI

from ../app import *
from ../generate import CLI

res = requests.get("http://localhost:8000/openapi.json")

with open("../openapi.json", "w") as f:
    f.write(res.content.decode("utf-8"))
###



def run_server():
    uvicorn.run(app)


@pytest.fixture
def server():
    proc = Process(target=run_server, args=(), daemon=True)
    proc.start()
    yield
    proc.kill() # Cleanup after test


def test_read_main(server):
    response = requests.get("http://localhost:8000/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

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

def test_predict():
    CLI.copy_server_files("examples/mouse_and_cheese")
    predict()
