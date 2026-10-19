"""
Application factory.

A factory (`create_app`) rather than a global instance: the tests build their
own application, configured separately, without duplicating the setup.
"""

import logging

from flask import Flask
from flask_cors import CORS

from .config import Config
from .controllers.health_controller import health_bp
from .extensions import socketio, spec
from .utils import database, errors, logs, request_logs, security_headers

logger = logging.getLogger(__name__)

SECRET_KEY_MIN_LENGTH = 32
MAX_BODY_SIZE_BYTES = 1024 * 1024


def create_app(config: type[Config] = Config) -> Flask:
    logs.configure(config.LOG_LEVEL)

    app = Flask(__name__)
    app.config.from_object(config)
    # Beyond this size, 413: a huge upload cannot saturate the memory.
    app.config["MAX_CONTENT_LENGTH"] = MAX_BODY_SIZE_BYTES

    if len(config.SECRET_KEY) < SECRET_KEY_MIN_LENGTH:
        logger.warning(
            "FLASK_SECRET_KEY too short (32 characters minimum), see .env.example",
            extra={"context": {"length": len(config.SECRET_KEY)}},
        )

    database.initialize(config.DATABASE_URL)

    # supports_credentials: the browser sends the session cookie with front-end calls.
    CORS(app, resources={r"/*": {"origins": config.CORS_ORIGINS}}, supports_credentials=True)
    socketio.init_app(app, cors_allowed_origins=config.CORS_ORIGINS)

    # Registers the real-time event handlers.
    from . import sockets  # noqa: F401

    # Request logging first, so that requests refused later are logged too.
    request_logs.install(app)
    security_headers.install(app)
    errors.register_handlers(app)

    # --- Routes: one Blueprint per resource ----------------------------------
    app.register_blueprint(health_bp)

    # After the Blueprints: the documentation describes the registered routes.
    spec.register(app)

    logger.info("Application started", extra={"context": {"corsOrigins": config.CORS_ORIGINS}})
    return app
