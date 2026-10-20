"""The logged-in user's own account."""

from flask import Blueprint, jsonify, request
from flask_pydantic_spec import Response

from ..dtos.auth_dto import UpdateProfileBody, UserDto, user_to_dto
from ..dtos.base import ErrorDto
from ..extensions import spec
from ..services import user_service
from ..services.user_service import ProfileChanges
from ..utils.access import current_user_id, require_login

user_bp = Blueprint("users", __name__, url_prefix="/users")


@user_bp.patch("/me")
@require_login()
@spec.validate(
    body=UpdateProfileBody,
    resp=Response(HTTP_200=UserDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_409=ErrorDto, HTTP_422=ErrorDto),
    tags=["Compte"],
)
def update_me():
    """Changes the name, e-mail, accessibility need (rider) or password.

    Only the fields sent are changed. A new password requires the current one.
    """
    body: UpdateProfileBody = request.context.body
    # model_fields_set: the fields actually sent, to tell "not sent" from null.
    changes = ProfileChanges(**{name: getattr(body, name) for name in body.model_fields_set})
    return jsonify(user_to_dto(user_service.update_profile(current_user_id(), changes)).to_json()), 200
