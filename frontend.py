import json

import requests
import streamlit as st


def run_the_app():

    st.sidebar.markdown("# Server location (URL)")

    url = st.sidebar.text_input("URL", "http://localhost:8000")

    st.sidebar.markdown("# Server authentication")

    auth = None
    user = st.sidebar.text_input("User name")
    password = st.sidebar.text_input("Password")
    if user and password:
        auth = (user, password)

    st.markdown("# Pathmind Policy Server")

    schema = server_schema(auth, url).json()
    print(schema)

    st.markdown("## Predictions")

    obs = generate_frontend_from_observations(schema)
    predict_button = st.button("Get prediction")
    if obs and auth and predict_button:
        response = predict(obs, auth, url).json()
        st.markdown(f"## Action: {response.get('actions')[0]}")
        st.markdown(f"## Probability: {int(100 *response.get('probability'))}%")

    # compute_action_distro = st.checkbox(label="What's the variance of my actions?", value=False)
    # if compute_action_distro and obs:
    #     distro_dict: dict = distro(obs, auth, url).json()
    #
    #     import matplotlib.pyplot as plt
    #     import numpy as np
    #     arr = np.asarray(list(distro_dict.values()))
    #     x_range = np.arange(len(distro_dict))
    #     plt.bar(x_range, arr)
    #     plt.xticks(x_range, list(distro_dict.keys()))
    #     st.pyplot(plt)


def server_schema(auth, url):
    return requests.get(f"{url}/schema", auth=auth)


def distro(observation, auth, url):
    return requests.post(f"{url}/distribution", json=observation, auth=auth)


def predict(observation, auth, url):
    return requests.post(f"{url}/predict/", json=observation, auth=auth)


def generate_frontend_from_observations(schema: dict):
    """Auto-generates front-end components from schema.

    :param schema: "Observation" schema loaded from YAML file
    :return: observation dictionary ready to be sent to server for processing.
    """
    properties = schema.get("observations")
    result = {}
    for key, values in properties.items():
        prop_type = values.get("type")
        # example = values.get("example")
        # description = values.get("description")
        if prop_type == "bool":
            val = st.checkbox(label=key, value=True)
        elif prop_type == "int":
            val = int(st.number_input(label=key, value=0))
            check_min_max(values, val)
        elif prop_type == "float":
            val = st.number_input(label=key, value=0.0)
            check_min_max(values, val)
        elif prop_type in ["List[int]", "List[float]", "List[bool]"]:
            val = json.loads(st.text_input(label=key, value=str([0])))
            validate_list_items(values, val)
            check_min_max_items(values, val)
        else:
            raise Exception(
                f"Unsupported data type {prop_type} in YAML schema for model server."
            )
        result[key] = val
    return result


def validate_list_items(values, val):
    items_type = values.get("type")
    if items_type == "integer":
        assert all(isinstance(v, int) for v in val), "All list items must be integers."
    elif items_type == "number":
        assert all(
            isinstance(v, float) for v in val
        ), "All list items must be floating point numbers."


def check_min_max_items(values, val):
    if "minItems" in values.keys():
        assert len(val) >= values.get(
            "minItems"
        ), f"Array too small, expected at least {values.get('minItems')} items."
    if "maxItems" in values.keys():
        assert len(val) <= values.get(
            "maxItems"
        ), f"Array too large, expected at most {values.get('maxItems')} items."


def check_min_max(values, val):
    if "minimum" in values.keys():
        assert val >= values.get(
            "minimum"
        ), f"value {val} too small, expected a minimum of {values.get('minimum')}."
    if "maximum" in values.keys():
        assert val <= values.get(
            "maximum"
        ), f"value {val} too large, expected a maximum of {values.get('maximum')}."


if __name__ == "__main__":
    run_the_app()
