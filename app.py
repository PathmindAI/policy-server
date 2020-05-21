import os
from flask import redirect
from flask_cors import CORS
import connexion


app = connexion.App(__name__, specification_dir='./')
app.add_api('swagger.yaml', strict_validation=True)
cors = CORS(app.app)
app.app.config["UPLOAD_FOLDER"] = "."


@app.route('/')
def home():
    return redirect("/api/ui", code=302)


if __name__ == "__main__":
    # app.debug = True
    app.run(host="0.0.0.0", port=8080)
