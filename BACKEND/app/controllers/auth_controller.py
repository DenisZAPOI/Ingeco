"""
Registration, login, activation, session renewal and logout.

The session lives in HttpOnly cookies (see utils/access.py): every route that
opens a session sets them on its response.
"""

from flask import Blueprint, jsonify, make_response, request
from flask_pydantic_spec import Response

from ..dtos.auth_dto import (
    ActivateBody,
    ConfirmRegistrationBody,
    LoginBody,
    RegisterBody,
    RegistrationCodeDto,
    UserDto,
    user_to_dto,
)
from ..dtos.base import ErrorDto
from ..extensions import spec
from ..repository.user_repository import User
from ..services import auth_service
from ..utils.access import (
    check_logout_csrf,
    current_user_id,
    end_session,
    refresh_account,
    renew_access,
    require_login,
    start_session,
)
from ..utils.errors import Unauthorized

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

_TAGS = ["Authentification"]


def _session_response(user: User, status: int):
    response = jsonify(user_to_dto(user).to_json())
    start_session(response, user)
    return response, status


@auth_bp.post("/register")
@spec.validate(
    body=RegisterBody,
    resp=Response(HTTP_202=RegistrationCodeDto, HTTP_400=ErrorDto, HTTP_429=ErrorDto),
    tags=_TAGS,
)
def register():
    """First step of a rider registration: sends a 6-digit code by SMS, valid 10 minutes.

    Nothing is created yet: POST /auth/register/confirm with the code creates
    the account. Same answer whether the number has an account or not (the
    SMS then says so). Sent again, it replaces the code. 429 after 3 codes
    an hour for a number, or 10 for a network address.

    Drivers, partners, operators and administrators are created by an
    administrator, never here.
    """
    body: RegisterBody = request.context.body
    sent = auth_service.start_registration(
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
        password=body.password,
        email=body.email,
        needs_accessible_vehicle=body.needs_accessible_vehicle,
        client_address=request.remote_addr,
    )
    return jsonify(RegistrationCodeDto(expires_at=sent.expires_at).to_json()), 202


@auth_bp.post("/register/confirm")
@spec.validate(
    body=ConfirmRegistrationBody,
    resp=Response(HTTP_201=UserDto, HTTP_400=ErrorDto, HTTP_409=ErrorDto, HTTP_422=ErrorDto),
    tags=_TAGS,
)
def confirm_registration():
    """Second step: the code received by SMS creates the rider account and opens the session.

    422 for a wrong or expired code (after 5, ask for a new one); 409 if the
    e-mail is already used by another account.
    """
    body: ConfirmRegistrationBody = request.context.body
    return _session_response(auth_service.confirm_registration(body.phone, body.code), 201)


@auth_bp.post("/login")
@spec.validate(
    body=LoginBody,
    resp=Response(HTTP_200=UserDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_429=ErrorDto),
    tags=_TAGS,
)
def login():
    """Phone + password. 429 after 5 failures in 15 minutes for the same number, or 30 from the same network address."""
    body: LoginBody = request.context.body
    return _session_response(auth_service.login(body.phone, body.password, request.remote_addr), 200)


@auth_bp.post("/activate")
@spec.validate(
    body=ActivateBody,
    resp=Response(HTTP_200=UserDto, HTTP_400=ErrorDto, HTTP_403=ErrorDto, HTTP_422=ErrorDto, HTTP_429=ErrorDto),
    tags=_TAGS,
)
def activate():
    """Phone + activation code + new password, then opens the session.

    429 after 5 failures in 15 minutes for the same number, or 30 from the same network address.
    """
    body: ActivateBody = request.context.body
    return _session_response(auth_service.activate(body.phone, body.code, body.password, request.remote_addr), 200)


@auth_bp.post("/refresh")
@spec.validate(resp=Response(HTTP_200=UserDto, HTTP_401=ErrorDto), tags=_TAGS)
def refresh():
    """New access token, from the refresh cookie (and its CSRF header).

    Rereads the account: a suspended or removed account, or a session opened
    before the last password change, is logged out here.
    """
    try:
        user = refresh_account()
    except Unauthorized as error:
        response = jsonify({"error": error.error, "detail": error.detail})
        end_session(response)
        return response, error.code

    response = jsonify(user_to_dto(user).to_json())
    renew_access(response, user)
    return response, 200


@auth_bp.post("/logout")
@spec.validate(resp=Response(HTTP_204=None, HTTP_401=ErrorDto), tags=_TAGS)
def logout():
    """Erases the session cookies. Works even with an expired session.

    401 if the CSRF header does not match the CSRF cookie (a forged request).
    """
    check_logout_csrf()
    response = make_response("", 204)
    end_session(response)
    return response


@auth_bp.get("/me")
@require_login()
@spec.validate(resp=Response(HTTP_200=UserDto, HTTP_401=ErrorDto), tags=_TAGS)
def me():
    """The logged-in account."""
    return jsonify(user_to_dto(auth_service.session_user(current_user_id())).to_json()), 200
