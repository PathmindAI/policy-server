"""This assumes the server is fully configured for the LPoC example"""
import timeit
import requests


data = {
  "coordinates": [
    1,
    1
  ],
  "has_core": True,
  "has_down_neighbour": True,
  "has_left_neighbour": True,
  "has_right_neighbour": True,
  "has_up_neighbour": True,
  "id": 0,
  "is_down_free": True,
  "is_left_free": False,
  "is_right_free": True,
  "is_up_free": True,
  "name": "pt07_c",
  "target": [
    6,
    2
  ]
}


def predict():
    return requests.post("https://localhost:8080/api/predict", verify=False, auth=("foo", "bar"), json=data)


predict()
number = 1000
res = timeit.timeit(predict, number=1000)
print(f"A total of {number} requests took {res} milliseconds to process on average.")

