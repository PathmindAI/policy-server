![pathmind policy server](assets/policy_server_logo.jpg)

## Overview

Pathmind's policy serving solution. It leverages a open source technologies
to quickly specify and run a lean web applications that serves one or several
reinforcement learning policies.


## How does it work?

![architecture](assets/server_backend_v2.jpg)

The user needs to specify one `schema.yaml` file that describes how an _observation_
looks like for their model. We call this input a schema. Once the schema is provided,
`FastAPI` will generate a `pydantic`-validated, OpenAPI-compliant endpoint for any
`saved_model.zip` model file that takes in observations as specified.

### FastAPI, uvicorn and Ray serve

The main work horse is the backend application that you can start locally with `uvicorn app:app`.
This will start a uvicorn server for `FastAPI` which is internally dispatched to a `Ray serve`
handle for predictions.

### Swagger UI & documentation

We leverage Swagger UI to fully describe, validate and test this API. The following endpoints
are exposed.

### Endpoints

- `/predict` To receive model predictions (once the first three endpoints have been used).
- `/clients` To download SDKs in several languages (currently Python, Java, Scala, R).
- `/docs` Get swagger UI classic documentation of the endpoint.
- `/redoc` Get `redoc` documentation for the endpoint.
- `/predict_deterministic` Get the most likely output every time, only works for non-tuple and discrete actions.
- `/distribution` Get the action likelihood distribution for non-tuple and discrete actions.

### Frontend

The frontend application found at `frontend.py` is a streamlit application that's just
there to demonstrate (very roughly) the application flow, i.e. how to use the backend,
for integration in the Pathmind web app. One noteworthy feature is that the form data
for observation inputs is generated on the fly as well (frontend for backend approach).
We also visualize the action distribution for a given observation, by probing the API,
which is another feature that should make it into the Pathmind app.

### CLI

Lastly, we also auto-generate a CLI from `generate.py` using Google's `fire` library.

## Install

```bash
virtualenv venv && source venv/bin/activate
pip install -r requirements.txt
```

Also, make sure you have `swagger-codegen` installed on your system, 
following [these instructions](https://swagger.io/docs/open-source-tools/swagger-codegen/).


## Run locally

Simply run

```commandline
uvicorn app:app
```

ray start --head --metrics-export-port=8080



## Run frontend (which starts the backend)

Simply running

```bash
streamlit run frontend.py
```

will start the app on [localhost:8501](localhost:8501) for testing. The application
should be self-explanatory. It leverages the `lpoc` example from the `examples` folder,
but can be used with any other model. Once you hit the `Start the server from schema`
button in the UI, you can also access the backend service directly at 
[localhost:8080](localhost:8000).

## Run backend only

```bash
uvicorn app:app
```

for a more production-ready web server. Both variants will start the backend at
[localhost:8080](localhost:8000), which comes with its own, self-contained UI.



## CLI

### Generate swagger.yaml from schema

This also generates all clients automatically under the hood.

```bash
python generate.py schema examples/lpoc/schema.yaml
```

### Generate clients

```bash
python generate.py clients
```

### Clean all local files (reset configuration)

```bash
python generate.py clean
```

## Docker

Build the container with

```bash
docker build . -t model
```

then run the image with

```bash
docker run  -p 8080:8080 model
```

