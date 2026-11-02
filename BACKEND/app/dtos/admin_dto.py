"""Bodies, queries and responses of /admin/users."""

import base64
import binascii
from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from ..repository.user_repository import Position, User, Vehicle
from ..services import account_rules
from ..services.account_rules import (
    EMAIL_MAX_LENGTH,
    MAX_SEATS,
    MIN_SEATS,
    MODEL_MAX_LENGTH,
    NAME_MAX_LENGTH,
    PLATE_MAX_LENGTH,
    SEARCH_MAX_LENGTH,
)
from ..services.admin_service import PHOTO_MAX_BYTES, AccountPage, ActivationCode
from . import cursor
from .auth_dto import PHONE_MAX_LENGTH, UserDto, user_to_dto
from .base import ApiModel, InputModel, apply_rule, field_error

Role = Literal["rider", "driver", "partner", "operator", "admin"]
# Partner referents come with the vouchers (step 5).
StaffRole = Literal["driver", "operator", "admin"]
Status = Literal["active", "suspended"]

# Base64 writes 4 characters for every 3 bytes: room for the largest photo accepted.
_BASE64_BLOCK_CHARS, _BASE64_BLOCK_BYTES = 4, 3
PHOTO_MAX_BASE64_LENGTH = (PHOTO_MAX_BYTES // _BASE64_BLOCK_BYTES + 1) * _BASE64_BLOCK_CHARS


# --- Request bodies and queries ----------------------------------------------

class VehicleBody(InputModel):
    plate: str = Field(max_length=PLATE_MAX_LENGTH, examples=["AB-123-CD"])
    model: str = Field(max_length=MODEL_MAX_LENGTH, examples=["Renault Kangoo"])
    seats: int = Field(ge=MIN_SEATS, le=MAX_SEATS, examples=[4])
    is_accessible: bool

    @field_validator("plate")
    @classmethod
    def _plate(cls, value: str) -> str:
        return apply_rule(account_rules.clean_plate, value)

    @field_validator("model")
    @classmethod
    def _model(cls, value: str) -> str:
        return apply_rule(account_rules.clean_name, value)

    def to_vehicle(self) -> Vehicle:
        return Vehicle(plate=self.plate, model=self.model, seats=self.seats, is_accessible=self.is_accessible)


class AccountListQuery(InputModel):
    # A phone number (its start, as typed: « 0694 12 ») or a name (contained).
    search: str | None = Field(None, max_length=SEARCH_MAX_LENGTH)
    role: Role | None = None
    status: Status | None = None
    # nextCursor of the previous page; absent for the first one.
    cursor: str | None = None

    @field_validator("search", mode="before")
    @classmethod
    def _search_as_text(cls, value: object) -> object:
        # The query string parser reads « 0694000003 » as a number.
        return str(value) if isinstance(value, int) else value

    @field_validator("search")
    @classmethod
    def _search(cls, value: str | None) -> str | None:
        # An empty search box means "no search".
        if value is None or not value.strip():
            return None
        return value.strip()

    @field_validator("cursor")
    @classmethod
    def _cursor(cls, value: str | None) -> str | None:
        if value is not None:
            apply_rule(cursor.decode, value)
        return value

    def position(self) -> Position | None:
        if self.cursor is None:
            return None
        created_at, user_id = cursor.decode(self.cursor)
        return Position(created_at=created_at, user_id=user_id)


class CreateAccountBody(InputModel):
    role: StaffRole
    first_name: str = Field(max_length=NAME_MAX_LENGTH)
    last_name: str = Field(max_length=NAME_MAX_LENGTH)
    phone: str = Field(max_length=PHONE_MAX_LENGTH, examples=["0694 12 34 56"])
    email: str | None = Field(None, max_length=EMAIL_MAX_LENGTH)
    # Required for a driver, refused for the other roles.
    vehicle: VehicleBody | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def _name(cls, value: str) -> str:
        return apply_rule(account_rules.clean_name, value)

    @field_validator("phone")
    @classmethod
    def _phone(cls, value: str) -> str:
        return apply_rule(account_rules.normalize_phone, value)

    @field_validator("email")
    @classmethod
    def _email(cls, value: str | None) -> str | None:
        return apply_rule(account_rules.clean_email, value)


class UpdateAccountBody(InputModel):
    """Only the fields sent are changed."""

    status: Status | None = None
    # rider only
    is_priority: bool | None = None
    # driver only
    vehicle: VehicleBody | None = None

    @field_validator("status", "is_priority", "vehicle")
    @classmethod
    def _not_null(cls, value):
        if value is None:
            raise field_error("Valeur invalide.")
        return value


class PhotoBody(InputModel):
    # JPEG reduced by the browser (~15 KB), in base64: the API stores it as is.
    image_base64: str = Field(max_length=PHOTO_MAX_BASE64_LENGTH)

    def image(self) -> bytes:
        try:
            return base64.b64decode(self.image_base64, validate=True)
        except binascii.Error:
            return b""


# --- Responses ---------------------------------------------------------------

class AccountDto(UserDto):
    """An account seen by an administrator: the user, and where its access stands."""

    # false: no password yet (created by someone else, never activated).
    is_activated: bool
    # End of validity of the current activation code; null without one.
    activation_code_expires_at: datetime | None
    # driver: when the photo was saved, null without one. Sent back in the
    # photo address (?v=…) so the browser cache follows a new photo.
    photo_updated_at: datetime | None


class AccountListDto(ApiModel):
    items: list[AccountDto]
    # To send back as `cursor` for the next page; null on the last page.
    next_cursor: str | None


class ActivationCodeDto(ApiModel):
    # Shown once: it cannot be read again, only replaced.
    code: str = Field(examples=["12345678"])
    expires_at: datetime


class CreatedAccountDto(ApiModel):
    account: AccountDto
    activation: ActivationCodeDto


def account_to_dto(user: User) -> AccountDto:
    return AccountDto(
        **user_to_dto(user).model_dump(),
        is_activated=user.password_hash is not None,
        activation_code_expires_at=user.activation_code_expires_at,
        photo_updated_at=user.photo_updated_at,
    )


def account_page_to_dto(page: AccountPage) -> AccountListDto:
    position = page.next_position
    return AccountListDto(
        items=[account_to_dto(user) for user in page.users],
        next_cursor=cursor.encode(position.created_at, position.user_id) if position else None,
    )


def activation_to_dto(activation: ActivationCode) -> ActivationCodeDto:
    return ActivationCodeDto(code=activation.code, expires_at=activation.expires_at)
