"""
Registration, login, activation, session renewal and logout.

The session lives in HttpOnly cookies (see utils/access.py): every route that
opens a session sets them on its response.
"""

from flask import Blueprint, jsonify, make_response, request
from flask_pydantic_spec import Response

from ..dtos.auth_dto import ActivateBody, LoginBody, RegisterBody, UserDto, user_to_dto
from ..dtos.base import ErrorDto
from ..extensions import spec
from ..repository.user_repository import User
from ..services import auth_service
from ..utils.access import current_user_id, end_session, refresh_identity, renew_access, require_login, start_session
from ..utils.errors import Unauthorized

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

_TAGS = ["Authentification"]


def _session_response(user: User, status: int):
    response = jsonify(user_to_dto(user).to_json())
    start_session(response, user.id, user.role)
    return response, status


@auth_bp.post("/register")
@spec.validate(
    body=RegisterBody,
    resp=Response(HTTP_201=UserDto, HTTP_400=ErrorDto, HTTP_409=ErrorDto),
    tags=_TAGS,
)
def register():
    """Creates a rider account and opens the session.

    Drivers, partners, operators and administrators are created by an
    administrator, never here.
    """
    body: RegisterBody = request.context.body
    user = auth_service.register_rider(
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
        password=body.password,
        email=body.email,
        needs_accessible_vehicle=body.needs_accessible_vehicle,
    )
    return _session_response(user, 201)


@auth_bp.post("/login")
@spec.validate(
    body=LoginBody,
    resp=Response(HTTP_200=UserDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_429=ErrorDto),
    tags=_TAGS,
)
def login():
    """Phone + password. 429 after 5 failures in 15 minutes for the same number."""
    body: LoginBody = request.context.body
    return _session_response(auth_service.login(body.phone, body.password), 200)


@auth_bp.post("/activate")
@spec.validate(
    body=ActivateBody,
    resp=Response(HTTP_200=UserDto, HTTP_400=ErrorDto, HTTP_403=ErrorDto, HTTP_422=ErrorDto, HTTP_429=ErrorDto),
    tags=_TAGS,
)
def activate():
    """Phone + activation code + new password, then opens the session."""
    body: ActivateBody = request.context.body
    return _session_response(auth_service.activate(body.phone, body.code, body.password), 200)


@auth_bp.post("/refresh")
@spec.validate(resp=Response(HTTP_200=UserDto, HTTP_401=ErrorDto), tags=_TAGS)
def refresh():
    """New access token, from the refresh cookie (and its CSRF header).

    Rereads the account: a suspended or removed account is logged out here.
    """
    user_id = refresh_identity()
    try:
        user = auth_service.session_user(user_id)
    except Unauthorized as error:
        response = jsonify({"error": error.error, "detail": error.detail})
        end_session(response)
        return response, error.code

    response = jsonify(user_to_dto(user).to_json())
    renew_access(response, user.id, user.role)
    return response, 200


@auth_bp.post("/logout")
@spec.validate(resp=Response(HTTP_204=None), tags=_TAGS)
def logout():
    """Erases the session cookies. Works even with an expired session."""
    response = make_response("", 204)
    end_session(response)
    return response


@auth_bp.get("/me")
@require_login()
@spec.validate(resp=Response(HTTP_200=UserDto, HTTP_401=ErrorDto), tags=_TAGS)
def me():
    """The logged-in account."""
    return jsonify(user_to_dto(auth_service.session_user(current_user_id())).to_json()), 200
