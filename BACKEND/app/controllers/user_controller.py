"""The logged-in user's own account."""

from flask import Blueprint, jsonify, request
from flask_pydantic_spec import Response

from ..dtos.auth_dto import UpdateProfileBody, UserDto, user_to_dto
from ..dtos.base import ErrorDto
from ..dtos.privacy_dto import DeletionRequestDto, MyDataDto, my_data_to_dto
from ..extensions import spec
from ..services import deletion_service, my_data_service, user_service
from ..services.user_service import ProfileChanges
from ..utils.access import current_user_id, require_login, start_session

# Who may ask to delete their account: the staff accounts are managed by an administrator.
_MAY_DELETE = ("rider", "driver")
_PRIVACY_TAGS = ["Mes données"]

user_bp = Blueprint("users", __name__, url_prefix="/users")


@user_bp.patch("/me")
@require_login()
@spec.validate(
    body=UpdateProfileBody,
    resp=Response(
        HTTP_200=UserDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_409=ErrorDto, HTTP_422=ErrorDto, HTTP_429=ErrorDto
    ),
    tags=["Compte"],
)
def update_me():
    """Changes the name, e-mail, accessibility need (rider) or password.

    Only the fields sent are changed. A new password requires the current one,
    and ends the sessions of the other phones: this one gets new cookies.
    429 after 5 wrong current passwords in 15 minutes.
    """
    body: UpdateProfileBody = request.context.body
    # model_fields_set: the fields actually sent, to tell "not sent" from null.
    changes = ProfileChanges(**{name: getattr(body, name) for name in body.model_fields_set})
    user = user_service.update_profile(current_user_id(), changes)
    response = jsonify(user_to_dto(user).to_json())
    if changes.new_password is not None:
        start_session(response, user)
    return response, 200


@user_bp.get("/me/data")
@require_login()
@spec.validate(resp=Response(HTTP_200=MyDataDto, HTTP_401=ErrorDto), tags=_PRIVACY_TAGS)
def my_data():
    """« Mes données » : everything the application keeps about the caller (RGPD art. 15 and 20)."""
    data = my_data_service.my_data(current_user_id())
    return jsonify(my_data_to_dto(data).to_json()), 200


@user_bp.get("/me/deletion-request")
@require_login(*_MAY_DELETE)
@spec.validate(
    resp=Response(HTTP_200=DeletionRequestDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto),
    tags=_PRIVACY_TAGS,
)
def get_deletion_request():
    """The caller's request to delete their account, waiting for an administrator; 404 without one."""
    requested_at = deletion_service.deletion_requested_at(current_user_id())
    return jsonify(DeletionRequestDto(requested_at=requested_at).to_json()), 200


@user_bp.post("/me/deletion-request")
@require_login(*_MAY_DELETE)
@spec.validate(
    resp=Response(HTTP_200=DeletionRequestDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto),
    tags=_PRIVACY_TAGS,
)
def request_deletion():
    """Asks to delete the account (RGPD art. 17). An administrator handles it by
    anonymising the account. Asking again returns the first request."""
    requested_at = deletion_service.request_deletion(current_user_id())
    return jsonify(DeletionRequestDto(requested_at=requested_at).to_json()), 200


@user_bp.delete("/me/deletion-request")
@require_login(*_MAY_DELETE)
@spec.validate(resp=Response(HTTP_204=None, HTTP_401=ErrorDto, HTTP_403=ErrorDto), tags=_PRIVACY_TAGS)
def withdraw_deletion_request():
    """Withdraws the request before an administrator handles it. Without one, nothing happens."""
    deletion_service.withdraw_request(current_user_id())
    return "", 204
