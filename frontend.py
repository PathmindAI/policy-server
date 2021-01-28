import streamlit as st
import json
import yaml
import requests
import subprocess
import os

import config
from generate import CLI

BASE_URL = 'http://localhost:8000'


@st.cache()
def start_server_process():
    # Spawns a gunicorn production web server with 4 workers.
    cmd = "uvicorn app:app"
    # Note: this won't work on GCP and generally this should be done differently eventually.
    subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)


def run_the_app():

    st.markdown("# Pathmind Policy Server")

    st.markdown("## Pick your use case:")

    model = st.selectbox('Which model would you like to try?',
                                 ('leuphana', 'lpoc', 'lpoc_tuple', 'mouse_and_cheese',
                                  'product_delivery', 'rail_drl', 'simple_scheduling',
                                  'simple_stochastic_tuple', 'zinc_factory'))

    path = os.path.abspath(f"./examples/{model}")
    # Copy model and schema to base folder,
    CLI.copy_server_files(path=path)

    # load the schema
    with open(config.PATHMIND_SCHEMA, 'r') as f:
        schema_str = f.read()
    schema = yaml.safe_load(schema_str)

    start_server = st.button('Start server from schema')
    if start_server:
        with st.spinner('Waiting for server to start'):
            # then start the server-side subprocess.
            start_server_process()

    st.markdown("## Prediction")

    obs = generate_frontend_from_observations(schema)
    predict_button = st.button("Get prediction")
    if obs and predict_button:
        response = predict(obs).json()
        st.text(response)
        print(response)
        st.text(
            f"Actions: {response.get('actions')}, "
            f"Probability: {response.get('probability'):.2f} "
        )

    compute_action_distro = st.checkbox(label="What's the variance of my actions?", value=False)
    if compute_action_distro and obs:
        distro_dict: dict = distro(obs).json()
        print(distro_dict)

        import matplotlib.pyplot as plt
        import numpy as np
        arr = np.asarray(list(distro_dict.values()))
        x_range = np.arange(len(distro_dict))
        plt.bar(x_range, arr)
        plt.xticks(x_range, list(distro_dict.keys()))
        st.pyplot(plt)


def distro(observation):
    return requests.post(f"{BASE_URL}/distribution", json=observation)


def predict(observation):
    return requests.post(f"{BASE_URL}/predict", json=observation)


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
            raise Exception(f"Unsupported data type {prop_type} in YAML schema for model server.")
        result[key] = val
    return result


def validate_list_items(values, val):
    items_type = values.get("type")
    if items_type == "integer":
        assert all(isinstance(v, int) for v in val), "All list items must be integers."
    elif items_type == "number":
        assert all(isinstance(v, float) for v in val), "All list items must be floating point numbers."


def check_min_max_items(values, val):
    if "minItems" in values.keys():
        assert len(val) >= values.get("minItems"), f"Array too small, expected at least {values.get('minItems')} items."
    if "maxItems" in values.keys():
        assert len(val) <= values.get("maxItems"), f"Array too large, expected at most {values.get('maxItems')} items."


def check_min_max(values, val):
    if "minimum" in values.keys():
        assert val >= values.get("minimum"), f"value {val} too small, expected a minimum of {values.get('minimum')}."
    if "maximum" in values.keys():
        assert val <= values.get("maximum"),  f"value {val} too large, expected a maximum of {values.get('maximum')}."


if __name__ == "__main__":
    run_the_app()
