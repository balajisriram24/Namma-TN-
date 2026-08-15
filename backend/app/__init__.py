from flask import Flask
from flask_cors import CORS
from .config import Config
from .db import init_db
from .routes import api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGIN"]}})
    init_db()

    @app.get("/")
    def index():
        return {
            "status": "ok",
            "service": "NammaTN AI Civic Connect",
            "api_base": "/api",
        }

    app.register_blueprint(api, url_prefix="/api")
    return app
