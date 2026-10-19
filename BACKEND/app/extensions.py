"""
Instances shared by the whole application.

They are created here, without an application, then attached to it in
`create_app()`. Controllers and socket handlers import them from this module,
which avoids circular imports with main.py.
"""

from flask_jwt_extended import JWTManager
from flask_pydantic_spec import FlaskPydanticSpec
from flask_socketio import SocketIO

from .utils.errors import after_validation, before_validation

# async_mode="threading": works with the Flask development server and
# simple-websocket, without eventlet or gevent to install.
socketio = SocketIO(async_mode="threading")

# JWT in HttpOnly cookies, see utils/access.py.
jwt = JWTManager()

# OpenAPI documentation generated from the DTOs, served on /apidoc/swagger.
# The front-end generates its TypeScript types from /apidoc/openapi.json.
# 400 and not 422 (library default): 422 is kept for business rules.
spec = FlaskPydanticSpec(
    "flask",
    title="API En route pour l'emploi",
    version="0.1.0",
    ui="swagger",
    validation_error_code=400,
    before=before_validation,
    after=after_validation,
)
