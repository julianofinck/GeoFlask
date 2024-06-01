import os

from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import db, migrate
from .routes.geojson import geojson_bp
from .routes.ping import ping_bp
from .routes.upload import upload_bp


def create_app(config=None):

    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    if config is None:
        config = Config
    app.config.from_object(config)

    # Allow CORS
    # CORS(app, resources={r"/*": {"origins": "*"}})
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(upload_bp)
    app.register_blueprint(ping_bp)
    app.register_blueprint(geojson_bp)

    return app
