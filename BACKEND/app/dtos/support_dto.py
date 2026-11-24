"""Requests and responses of /help-requests ("Être rappelé", module M0)."""

from datetime import datetime

from pydantic import Field, field_validator

from ..repository.support_repository import SupportRequest
from ..services import account_rules
from .auth_dto import PHONE_MAX_LENGTH
from .base import ApiModel, InputModel, apply_rule


class CallbackBody(InputModel):
    # The number to call back: asked even when logged in, the person may
    # prefer another one (a relative's, a work phone).
    phone: str = Field(max_length=PHONE_MAX_LENGTH, examples=["0694 12 34 56"])

    @field_validator("phone")
    @classmethod
    def _phone(cls, value: str) -> str:
        return apply_rule(account_rules.normalize_phone, value)


class CallbackDto(ApiModel):
    """A callback to make, for an operator or an administrator."""

    id: int
    # Always set for a callback (migration 027); null only once its account is deleted.
    phone: str | None = Field(examples=["+594694123456"])
    # false: someone without an account asked.
    has_account: bool
    created_at: datetime


class CallbackListDto(ApiModel):
    # The oldest first: the first asked is the first called back.
    items: list[CallbackDto]


def callbacks_to_dto(requests: list[SupportRequest]) -> CallbackListDto:
    items = [_callback_to_dto(request) for request in requests]
    return CallbackListDto(items=items)


def _callback_to_dto(request: SupportRequest) -> CallbackDto:
    has_account = request.user_id is not None
    return CallbackDto(id=request.id, phone=request.phone, has_account=has_account, created_at=request.created_at)
