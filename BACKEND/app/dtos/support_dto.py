"""Requests of /help-requests ("Être rappelé", module M0)."""

from pydantic import Field, field_validator

from ..services import account_rules
from .auth_dto import PHONE_MAX_LENGTH
from .base import InputModel, apply_rule


class CallbackBody(InputModel):
    # The number to call back: asked even when logged in, the person may
    # prefer another one (a relative's, a work phone).
    phone: str = Field(max_length=PHONE_MAX_LENGTH, examples=["0694 12 34 56"])

    @field_validator("phone")
    @classmethod
    def _phone(cls, value: str) -> str:
        return apply_rule(account_rules.normalize_phone, value)
