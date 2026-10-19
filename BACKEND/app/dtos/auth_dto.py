"""Bodies and responses of /auth/* and /users/me."""

from datetime import datetime
from typing import Literal

from pydantic import Field, ValidationInfo, field_validator

from ..repository.user_repository import User
from ..services import account_rules
from ..services.account_rules import EMAIL_MAX_LENGTH, NAME_MAX_LENGTH, PASSWORD_MAX_LENGTH
from .base import ApiModel, InputModel, apply_rule, field_error

PHONE_MAX_LENGTH = 30  # room for spaces, dots and dashes typed by the user
CODE_MAX_LENGTH = 20


# --- Responses ---------------------------------------------------------------

class VehicleDto(ApiModel):
    plate: str
    model: str
    seats: int
    is_accessible: bool


class UserDto(ApiModel):
    """The logged-in account. Fields of another role are null."""

    id: int
    role: Literal["rider", "driver", "partner", "operator", "admin"]
    status: Literal["active", "suspended"]
    first_name: str
    last_name: str
    phone: str
    email: str | None
    # rider
    is_priority: bool | None
    needs_accessible_vehicle: bool | None
    # driver
    vehicle: VehicleDto | None
    # partner
    partner_id: int | None
    created_at: datetime


def user_to_dto(user: User) -> UserDto:
    is_rider = user.role == account_rules.RIDER
    vehicle = user.vehicle
    return UserDto(
        id=user.id,
        role=user.role,
        status=user.status,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        email=user.email,
        is_priority=user.is_priority if is_rider else None,
        needs_accessible_vehicle=user.needs_accessible_vehicle if is_rider else None,
        vehicle=(
            VehicleDto(plate=vehicle.plate, model=vehicle.model, seats=vehicle.seats, is_accessible=vehicle.is_accessible)
            if vehicle
            else None
        ),
        partner_id=user.partner_id,
        created_at=user.created_at,
    )


# --- Request bodies ----------------------------------------------------------

class _PhoneField(InputModel):
    phone: str = Field(max_length=PHONE_MAX_LENGTH, examples=["0694 12 34 56"])

    @field_validator("phone")
    @classmethod
    def _phone(cls, value: str) -> str:
        return apply_rule(account_rules.normalize_phone, value)


class RegisterBody(_PhoneField):
    first_name: str = Field(max_length=NAME_MAX_LENGTH)
    last_name: str = Field(max_length=NAME_MAX_LENGTH)
    password: str = Field(max_length=PASSWORD_MAX_LENGTH)
    email: str | None = Field(None, max_length=EMAIL_MAX_LENGTH)
    needs_accessible_vehicle: bool = False

    @field_validator("first_name", "last_name")
    @classmethod
    def _name(cls, value: str) -> str:
        return apply_rule(account_rules.clean_name, value)

    @field_validator("password")
    @classmethod
    def _password(cls, value: str) -> str:
        return apply_rule(account_rules.check_password_strength, value)

    @field_validator("email")
    @classmethod
    def _email(cls, value: str | None) -> str | None:
        return apply_rule(account_rules.clean_email, value)


class LoginBody(_PhoneField):
    # No strength rule here: only the stored hash decides.
    password: str = Field(min_length=1, max_length=PASSWORD_MAX_LENGTH)


class ActivateBody(_PhoneField):
    code: str = Field(max_length=CODE_MAX_LENGTH, examples=["1234 5678"])
    password: str = Field(max_length=PASSWORD_MAX_LENGTH)

    @field_validator("code")
    @classmethod
    def _code(cls, value: str) -> str:
        return apply_rule(account_rules.clean_activation_code, value)

    @field_validator("password")
    @classmethod
    def _password(cls, value: str) -> str:
        return apply_rule(account_rules.check_password_strength, value)


class UpdateProfileBody(InputModel):
    """Only the fields sent are changed. email: null removes the address."""

    first_name: str | None = Field(None, max_length=NAME_MAX_LENGTH)
    last_name: str | None = Field(None, max_length=NAME_MAX_LENGTH)
    email: str | None = Field(None, max_length=EMAIL_MAX_LENGTH)
    needs_accessible_vehicle: bool | None = None
    current_password: str | None = Field(None, max_length=PASSWORD_MAX_LENGTH)
    new_password: str | None = Field(None, max_length=PASSWORD_MAX_LENGTH)

    @field_validator("first_name", "last_name")
    @classmethod
    def _name(cls, value: str | None) -> str:
        if value is None:
            raise field_error("Ce champ est obligatoire.")
        return apply_rule(account_rules.clean_name, value)

    @field_validator("email")
    @classmethod
    def _email(cls, value: str | None) -> str | None:
        return apply_rule(account_rules.clean_email, value)

    @field_validator("needs_accessible_vehicle")
    @classmethod
    def _not_null(cls, value: bool | None) -> bool:
        if value is None:
            raise field_error("Valeur invalide.")
        return value

    @field_validator("new_password")
    @classmethod
    def _new_password(cls, value: str | None, info: ValidationInfo) -> str | None:
        if value is None:
            return None
        # current_password is declared first, so it is already in info.data.
        if not info.data.get("current_password"):
            raise field_error("Indiquez aussi votre mot de passe actuel.")
        return apply_rule(account_rules.check_password_strength, value)
