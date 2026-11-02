"""Administration of the accounts (UC51 to UC53). Administrators only."""

from flask import Blueprint, jsonify, make_response, request
from flask_pydantic_spec import Response

from ..dtos.admin_dto import (
    AccountDto,
    AccountListDto,
    AccountListQuery,
    ActivationCodeDto,
    CreateAccountBody,
    CreatedAccountDto,
    PhotoBody,
    UpdateAccountBody,
    account_page_to_dto,
    account_to_dto,
    activation_to_dto,
)
from ..dtos.base import ErrorDto
from ..extensions import spec
from ..services import admin_service
from ..services.admin_service import AccountChanges
from ..utils.access import current_user_id, require_login

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

_TAGS = ["Administration"]
_ADMIN = "admin"
# The photo address carries its date (?v=…): a new photo is a new address,
# so the browser may keep this one for long.
_PHOTO_CACHE = "private, max-age=86400"


@admin_bp.get("/users")
@require_login(_ADMIN)
@spec.validate(
    query=AccountListQuery,
    resp=Response(HTTP_200=AccountListDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto),
    tags=_TAGS,
)
def list_users():
    """Accounts, the newest first, 20 per page; send nextCursor back as cursor for the next page.

    search: the start of a phone number (« 0694 12 ») or part of a name.
    """
    query: AccountListQuery = request.context.query
    page = admin_service.list_accounts(
        search=query.search, role=query.role, status=query.status, after=query.position()
    )
    return jsonify(account_page_to_dto(page).to_json()), 200


@admin_bp.get("/users/<int:user_id>")
@require_login(_ADMIN)
@spec.validate(
    resp=Response(HTTP_200=AccountDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto),
    tags=_TAGS,
)
def get_user(user_id: int):
    """An account."""
    return jsonify(account_to_dto(admin_service.get_account(user_id)).to_json()), 200


@admin_bp.post("/users")
@require_login(_ADMIN)
@spec.validate(
    body=CreateAccountBody,
    resp=Response(
        HTTP_201=CreatedAccountDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_409=ErrorDto,
        HTTP_422=ErrorDto,
    ),
    tags=_TAGS,
)
def create_user():
    """Creates a driver (with their vehicle), an operator or an administrator, without password.

    The answer carries the activation code, valid 48 h, shown once: the
    person activates the account with it (POST /auth/activate).
    """
    body: CreateAccountBody = request.context.body
    user, activation = admin_service.create_account(
        admin_id=current_user_id(),
        role=body.role,
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
        email=body.email,
        vehicle=body.vehicle.to_vehicle() if body.vehicle else None,
    )
    dto = CreatedAccountDto(account=account_to_dto(user), activation=activation_to_dto(activation))
    return jsonify(dto.to_json()), 201


@admin_bp.patch("/users/<int:user_id>")
@require_login(_ADMIN)
@spec.validate(
    body=UpdateAccountBody,
    resp=Response(
        HTTP_200=AccountDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto,
        HTTP_409=ErrorDto, HTTP_422=ErrorDto,
    ),
    tags=_TAGS,
)
def update_user(user_id: int):
    """Suspends or reactivates, marks a rider as priority, changes a driver's vehicle.

    Only the fields sent are changed. A driver holding an accepted or started
    ride cannot be suspended (409); a suspended driver goes offline. A rider's
    rides not taken yet are cancelled and refunded; one accepted by a driver or
    started blocks the suspension (409).
    """
    body: UpdateAccountBody = request.context.body
    changes = AccountChanges(**{name: getattr(body, name) for name in body.model_fields_set})
    if body.vehicle is not None:
        changes.vehicle = body.vehicle.to_vehicle()
    user = admin_service.update_account(admin_id=current_user_id(), user_id=user_id, changes=changes)
    return jsonify(account_to_dto(user).to_json()), 200


@admin_bp.put("/users/<int:user_id>/photo")
@require_login(_ADMIN)
@spec.validate(
    body=PhotoBody,
    resp=Response(
        HTTP_200=AccountDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto,
        HTTP_422=ErrorDto,
    ),
    tags=_TAGS,
)
def put_photo(user_id: int):
    """Saves or replaces a driver's face photo: a JPEG already reduced by the browser (100 KB at most)."""
    body: PhotoBody = request.context.body
    user = admin_service.save_photo(admin_id=current_user_id(), user_id=user_id, image=body.image())
    return jsonify(account_to_dto(user).to_json()), 200


@admin_bp.get("/users/<int:user_id>/photo")
@require_login(_ADMIN)
@spec.validate(resp=Response(HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto), tags=_TAGS)
def get_photo(user_id: int):
    """The driver's photo (image/jpeg), to check it. 404 without one."""
    image, _updated_at = admin_service.get_photo(user_id)
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpeg"
    response.headers["Cache-Control"] = _PHOTO_CACHE
    return response


@admin_bp.post("/users/<int:user_id>/activation-code")
@require_login(_ADMIN)
@spec.validate(
    resp=Response(HTTP_201=ActivationCodeDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto),
    tags=_TAGS,
)
def new_activation_code(user_id: int):
    """A new activation code (first access or forgotten password), valid 48 h, shown once.

    It replaces the previous one. The current password keeps working until
    the person chooses a new one with the code.
    """
    activation = admin_service.new_activation_code(admin_id=current_user_id(), user_id=user_id)
    return jsonify(activation_to_dto(activation).to_json()), 201
