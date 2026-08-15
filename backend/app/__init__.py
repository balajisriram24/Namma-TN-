from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

from .config import Config
from .db import init_db
from .routes import api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["FRONTEND_ORIGIN"]
            }
        },
    )

    init_db()

    # React production build directory
    frontend_dist = (
        Path(__file__).resolve().parent.parent.parent
        / "frontend"
        / "dist"
    )

    @app.get("/")
    def index():
        return send_from_directory(frontend_dist, "index.html")

    @app.route("/<path:path>")
    def serve_frontend(path):
        file_path = frontend_dist / path

        if file_path.is_file():
            return send_from_directory(frontend_dist, path)

        return send_from_directory(frontend_dist, "index.html")

    app.register_blueprint(api, url_prefix="/api")

    return app