![pathmind policy server](assets/policy_server_logo.jpg)

## Overview

This is a prototype for Pathmind's policy serving solution. It leverages a few technologies
to quickly specify and run a web application that serves reinforcement learning policies.

## How does it work?

![architecture](assets/server_backend_v1.jpg)

The user needs to specify one `YAML` file or text input that describes how an _observation_
looks like for their model. We call this input a schema. Once the schema is provided, an
OpenAPI 2.0 compliant `swagger.yaml` file is generated from `swagger.template.yaml`.

We then use `connexion` to auto-generate an API for us in `app.py`. The API endpoint
functionality is implemented in `api.py`. Everything you might want to configure for this
application can be found in `configuration.py`, from application logic to web server
configuration.

The main work horse is the backend application that you can start with `python app.py`.
By default this runs a simple Flask app, but you can configure other ways of starting it.
We leverage Swagger UI to fully describe, validate and test this API. The following endpoints
are exposed:

- `/model`: Used to upload a TensorFlow (or PyTorch in later iterations) model.
- `/preprocessor`: To upload a Python script to preprocess model inputs.
- `/outputmapper`: To upload a `YAML` file that maps actions to their meanings.
- `/predict`: To receive model predictions (once the first three endpoints have been used).
- `/clients`: To download SDKs in several languages (currently Python, Java, Scala, R).

The frontend application found at `frontend.py` is a streamlit application that's just
there to demonstrate (very roughly) the application flow, i.e. how to use the backend,
for integration in the Pathmind web app. One noteworthy feature is that the form data
for observation inputs is generated on the fly as well (frontend for backend approach).
We also visualize the action distribution for a given observation, by probing the API,
which is another feature that should make it into the Pathmind app.

Lastly, we also auto-generate a CLI from `generate.py` using Google's `fire` library.

## Install

```bash
virtualenv venv && source venv/bin/activate
pip install -r requirements.txt
```

Also, make sure you have `swagger-codegen` installed on your system, 
following [these instructions](https://swagger.io/docs/open-source-tools/swagger-codegen/).

## Run frontend (which starts the backend)

Simply running

```bash
streamlit run frontend.py
```

will start the app on [localhost:8501](localhost:8501) for testing. The application
should be self-explanatory. It leverages the `lpoc` example from the `examples` folder,
but can be used with any other model. Once you hit the `Start the server from schema`
button in the UI, you can also access the backend service directly at 
[localhost:8080](localhost:8080).

## Run backend only

Either run

```bash
python app.py
```

for testing purposes (which starts a `Flask` app in debug mode) or run

```bash
gunicorn app:app -b :8080 -w 4
```

for a more production-ready web server. Both variants will start the backend at
[localhost:8080](localhost:8080), which comes with its own, self-contained UI.

## Run models with tuple or continuous actions

To tell Swagger to prepare a spec for a tuple model, either change `TUPLE` to `True` in `config.py` directly, or
simply work with environment variables (preferred):

```bash
TUPLE=True python generate.py schema examples/simple_stochastic_tuple/schema.yaml
TUPLE=True python app.py
```

The same goes for the frontend, which you should start with `TUPLE=True streamlit run frontend.py`.

Note that the same holds true for discrete vs. continuous actions, i.e. use the environment variable
`DISCRETE_ACTIONS=False` for continuous action models (defaults to `True`).

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

## Deploy on GCE

Just for demo purposes. Deploy the backend application with

```bash
gcloud app deploy
```

after creating a project on Google cloud console, confirm with `Y` when asked to and
watch the app live once deployed using

```bash
gcloud app browse
```

## TODOs and desiderata

- For faster inference, we might at some point want switch to TensorFlow Serving internally. 
Not necessarily difficult, just needs to be done. TF Serving has to be started separately,
resp. spawned as subprocess. By doing so the interface remains the same, while the requests
get redirected to TF Serving (API stability).
- TensorFlow GPU: for more complex models and if speed is a concern, we should allow GPU
resources to be leveraged. That can be done entirely dynamically, e.g. by setting the
right flags in Docker and spinning up a suitable AWS instance. 
- Proper SSL/TLS support. Probably best to simply front the whole app with a properly
configured nginx reverse proxy.
- Proper password management, e.g. OAuth support, instead of basic auth.
- PyTorch support. This can wait until we really need it.
- Do we need proper hot reloading of models? Right now you can upload a new model at any
point in time. This is unlikely to cause problems, but might lead to race conditions and
the app failing. Investigate this more thoroughly.


