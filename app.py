import config
import flask
import flask_cors
import connexion


# Start connexion app from the base path and add the API with strict validation.
app = connexion.App(__name__, specification_dir=config.BASE_PATH)
app.add_api(config.SWAGGER_FILE, base_path=config.API_PREFIX, strict_validation=True,
            validate_responses=False)

# Apply CORS headers and set the correct upload folder for the underlying Flask app.
cors = flask_cors.CORS(app.app)
app.app.config["UPLOAD_FOLDER"] = config.BASE_PATH
flask_app = app.app


@app.route('/')
def home():
    """Redirect home to Swagger UI"""
    return flask.redirect(f"{config.API_PREFIX}/ui", code=302)


if __name__ == "__main__":
    app.debug = config.DEBUG
    kwargs = config.get_server_arguments()
    app.run(**kwargs)
