"""
Application factory.

A factory (`create_app`) rather than a global instance: the tests build their
own application, configured separately, without duplicating the setup.
"""

import logging

from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config, UnsafeConfiguration
from .controllers.admin_controller import admin_bp
from .controllers.auth_controller import auth_bp
from .controllers.driver_controller import driver_bp
from .controllers.health_controller import health_bp
from .controllers.help_service_controller import help_service_bp
from .controllers.job_controller import job_bp
from .controllers.place_controller import place_bp
from .controllers.ride_controller import ride_bp
from .controllers.user_controller import user_bp
from .extensions import jwt, socketio, spec
from .repository import place_repository, ride_repository, user_repository
from .services import auth_service, expiry_service, place_service
from .utils import access, database, errors, logs, periodic, request_logs, security_headers

logger = logging.getLogger(__name__)

SECRET_KEY_MIN_LENGTH = 32
# The value of .env.example: a server started with it signs its tokens with a public key.
EXAMPLE_SECRET_KEY = "replace-with-a-generated-key"
MAX_BODY_SIZE_BYTES = 1024 * 1024
# The front and the API are on different origins: before each write, the
# browser asks the API for permission (OPTIONS). Kept 2 hours (Chrome's cap),
# so a write costs one round trip instead of two on a 2G network.
CORS_PREFLIGHT_MAX_AGE_SECONDS = 2 * 60 * 60
# Rides expire within a minute of their deadline (contract 6.8).
EXPIRY_INTERVAL_SECONDS = 60


def check_safety(config: type[Config]) -> None:
    """Refuses to start with settings that would expose a server.

    Secure cookies (COOKIE_SECURE, the default) mark a server reached over
    https, so a hosted one: no public demo accounts and no debug mode there.
    """
    # The tokens are signed with this key (HS256): a short one is found
    # offline from a single token, and then any role can be forged.
    if len(config.SECRET_KEY) < SECRET_KEY_MIN_LENGTH or config.SECRET_KEY == EXAMPLE_SECRET_KEY:
        raise UnsafeConfiguration(
            f"FLASK_SECRET_KEY must be generated, {SECRET_KEY_MIN_LENGTH} characters minimum: see .env.example."
        )
    if config.JWT_COOKIE_SECURE and config.LOAD_DEMO_DATA:
        raise UnsafeConfiguration("LOAD_DEMO_DATA=true is for local development only (COOKIE_SECURE=false).")
    if config.JWT_COOKIE_SECURE and config.DEBUG:
        raise UnsafeConfiguration("FLASK_DEBUG=true is for local development only (COOKIE_SECURE=false).")


def create_app(config: type[Config] = Config) -> Flask:
    logs.configure(config.LOG_LEVEL)
    check_safety(config)

    app = Flask(__name__)
    app.config.from_object(config)
    # Beyond this size, 413: a huge upload cannot saturate the memory.
    app.config["MAX_CONTENT_LENGTH"] = MAX_BODY_SIZE_BYTES
    if config.TRUSTED_PROXY_COUNT:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=config.TRUSTED_PROXY_COUNT)  # type: ignore[method-assign]

    database.initialize(config.DATABASE_URL)
    place_repository.configure(config.ORS_API_KEY)
    place_service.configure(signing_key=config.SECRET_KEY)
    if config.LOAD_DEMO_DATA:
        logger.warning("LOAD_DEMO_DATA: development accounts with a public password are loaded")
        user_repository.reset(demo_accounts=True)
        ride_repository.reset(dev_rides=True)

    # supports_credentials: the browser sends the session cookie with front-end calls.
    CORS(
        app,
        resources={r"/*": {"origins": config.CORS_ORIGINS}},
        supports_credentials=True,
        max_age=CORS_PREFLIGHT_MAX_AGE_SECONDS,
    )
    socketio.init_app(app, cors_allowed_origins=config.CORS_ORIGINS)
    jwt.init_app(app)
    access.register_jwt_callbacks(jwt)
    access.configure(auth_service.check_session)
    auth_service.configure(demo_codes=config.LOAD_DEMO_DATA)

    # Registers the real-time event handlers.
    from . import sockets  # noqa: F401

    # Request logging first, so that requests refused later are logged too.
    request_logs.install(app)
    security_headers.install(app, https=config.JWT_COOKIE_SECURE)
    errors.register_handlers(app)

    # --- Routes: one Blueprint per resource ----------------------------------
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(place_bp)
    app.register_blueprint(ride_bp)
    app.register_blueprint(driver_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(help_service_bp)

    # After the Blueprints: the documentation describes the registered routes.
    # Without API_DOCS_ENABLED the validation still works, /apidoc answers 404.
    spec.register(app, register_route=config.API_DOCS_ENABLED)

    if config.PERIODIC_TASKS_ENABLED:
        periodic.start(socketio, "expire_rides", EXPIRY_INTERVAL_SECONDS, expiry_service.expire_due_rides)

    logger.info("Application started", extra={"context": {"corsOrigins": config.CORS_ORIGINS}})
    return app
