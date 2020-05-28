import streamlit as st
import os
import json
import yaml
import requests
import subprocess

import config
from generate import CLI

PROTOCOL = "http://"
BASE_URL = f"{PROTOCOL}{config.HOST}:{config.PORT}/{config.API_PREFIX}"


@st.cache()
def load_schema(schema_str):
    return yaml.safe_load(schema_str)


@st.cache()
def start_server_process():
    # Spawns a gunicorn production web server with 4 workers.
    cmd = "gunicorn app:app -b :8080 -w 4"
    # Note: this won't work on GCP and generally this should be done differently eventually.
    subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)


def generate_sidebar():
    st.sidebar.markdown("# Server configuration")

    auth = None
    user = st.sidebar.text_input("User name")
    password = st.sidebar.text_input("Password")
    if user and password:
        auth = (user, password)

    schema_str = st.sidebar.text_area(label="Paste your observation schema", value=example_schema(), height=300)
    schema = {}
    if schema_str:
        schema = yaml.safe_load(schema_str)
        with open(config.SCHEMA_FILE, 'w') as f:
            f.write(schema_str)

        start_server = st.sidebar.button('Start server from schema')
        if start_server:
            with st.spinner('Waiting for server to start'):
                # Generate yaml schema so that the server can use it to spin up the API,
                CLI.schema(config.SCHEMA_FILE)
                # then start the server-side subprocess.
                start_server_process()

    return schema, auth


def run_the_app():

    schema, auth = generate_sidebar()

    st.markdown("# Pathmind Policy Server")

    need_uploads = st.checkbox(label="Need to upload model and processing files first?", value=False)
    if need_uploads:

        st.markdown("## Model upload")
        model_file = st.text_input("Path to model file", value='examples/lpoc/saved_model.zip')
        if model_file:
            model_button = st.button("Upload model")
            if model_button:
                response = upload_model(model_file, auth)
                st.text(response.text)

        st.markdown("## Preprocessor upload")
        preprocessor_file = st.text_input("Path to preprocessor file", value='examples/lpoc/preprocessor.py')
        if preprocessor_file:
            preprocessor_button = st.button("Upload preprocessor")
            if preprocessor_button:
                response = upload_preprocessor(preprocessor_file, auth)
                st.text(response.text)
                with open(config.PREPROCESSOR_FILE, 'r') as f:
                    st.text_area(label="Uploaded preprocessor:", value=f.read(), height=300)

        st.markdown("## Output mapper upload")
        output_file = st.text_input("Path to output mapper file", value='examples/lpoc/output.yaml')
        if output_file:
            output_button = st.button("Upload output mapper")
            if output_button:
                response = upload_output_mapper(output_file, auth)
                st.text(response.text)
                with open(config.OUTPUT_MAPPER_FILE, 'r') as f:
                    st.text_area(label="Uploaded output mapper:", value=f.read(), height=150)

    want_predictions = st.checkbox(label="Want to get predictions?", value=False)
    if want_predictions:
        st.markdown("## Prediction")

        obs = generate_frontend_from_observations(schema)
        predict_button = st.button("Get prediction")
        if obs and predict_button:
            response = predict(obs, auth).json()
            st.text(
                f"Action: {response.get('action')}, "
                f"Meaning: {response.get('meaning')}, "
                f"Probability: {response.get('probability'):.2f} "
            )

        compute_action_distro = st.checkbox(label="What's the variance of my actions?", value=False)
        if compute_action_distro and obs:
            distro_dict: dict = distro(obs, auth).json()

            import matplotlib.pyplot as plt
            import numpy as np
            arr = np.asarray(list(distro_dict.values()))
            x_range = np.arange(len(distro_dict))
            plt.bar(x_range, arr)
            plt.xticks(x_range, list(distro_dict.keys()))
            st.pyplot(plt)


def distro(observation, auth):
    return requests.post(f"{BASE_URL}/distro", json=observation, auth=auth)


def predict(observation, auth):
    return requests.post(f"{BASE_URL}/predict", json=observation, auth=auth)


def upload_model(model_file, auth):
    os.makedirs(config.MODEL_FOLDER, exist_ok=True)
    files = {'model_file': open(model_file, 'rb')}
    return requests.post(f"{BASE_URL}/model", files=files, auth=auth)


def upload_preprocessor(model_file, auth):
    files = {'preprocessor_file': open(model_file, 'rb')}
    return requests.post(f"{BASE_URL}/preprocessor", files=files, auth=auth)


def upload_output_mapper(model_file, auth):
    files = {'output_mapper_file': open(model_file, 'rb')}
    return requests.post(f"{BASE_URL}/outputmapper", files=files, auth=auth)


def generate_frontend_from_observations(schema: dict):
    """Auto-generates front-end components from schema.

    :param schema: "Observation" schema loaded from YAML file
    :return: observation dictionary ready to be sent to server for processing.
    """
    properties = schema.get("Observation").get("properties")
    result = {}
    for key, values in properties.items():
        prop_type = values.get("type")
        example = values.get("example")
        description = values.get("description")
        if prop_type == "boolean":
            val = st.checkbox(label=description, value=example)
        elif prop_type == "integer":
            val = int(st.number_input(label=description, value=example))
            check_min_max(values, val)
        elif prop_type == "number":
            val = st.number_input(label=description, value=example)
            check_min_max(values, val)
        elif prop_type == "array":
            val = json.loads(st.text_input(label=description, value=str(example)))
            validate_list_items(values, val)
            check_min_max_items(values, val)
        else:
            raise Exception(f"Unsupported data type {prop_type} in YAML schema for model server.")
        result[key] = val
    return result


def validate_list_items(values, val):
    items_type = values.get("items").get("type")
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


def example_schema():
    with open("examples/lpoc/schema.yaml") as f:
        return f.read()


if __name__ == "__main__":
    run_the_app()
