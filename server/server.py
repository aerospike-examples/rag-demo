from flask import Flask
from flask_cors import CORS

# The flask application.
app = Flask(__name__, static_url_path="", static_folder="dist")
CORS(app)

import routes

dir(routes)

if __name__ == "__main__":
    app.run(host="localhost", port=8080)
