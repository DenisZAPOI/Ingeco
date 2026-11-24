"""Responses about the person's own data (« Mes données », deletion of the account; audit RGPD R3)."""

from datetime import datetime
from typing import Literal

from pydantic import Field

from ..repository.deletion_repository import OpenRequest
from ..repository.support_repository import SupportRequest
from ..services.my_data_service import MyData
from .auth_dto import UserDto, user_to_dto
from .base import ApiModel
from .orientation_dto import PlanDto, plan_to_dto
from .ride_dto import RideDto, ride_to_dto


class DeletionRequestDto(ApiModel):
    requested_at: datetime


class HelpRequestDto(ApiModel):
    kind: Literal["callback", "report"]
    # The number given to be called back; null once erased.
    phone: str | None
    message: str | None
    created_at: datetime
    # null while nobody handled it.
    handled_at: datetime | None


class MyDataDto(ApiModel):
    """Everything the application keeps about the logged-in person."""

    account: UserDto
    # The most recently booked first, as the person sees them in the app.
    rides: list[RideDto]
    # A rider's current action plan, with the answers it comes from.
    plan: PlanDto | None
    help_requests: list[HelpRequestDto]
    # Set while a request to delete the account waits for an administrator.
    deletion_requested_at: datetime | None


class DeletionRequestItemDto(ApiModel):
    """An open request, for the administrator: enough to recognise the account."""

    user_id: int
    role: Literal["rider", "driver", "partner", "operator", "admin"]
    first_name: str
    last_name: str
    phone: str = Field(examples=["+594694123456"])
    requested_at: datetime


class DeletionRequestListDto(ApiModel):
    # The oldest first: the first sent is the first handled.
    items: list[DeletionRequestItemDto]


def my_data_to_dto(data: MyData) -> MyDataDto:
    return MyDataDto(
        account=user_to_dto(data.user),
        rides=[ride_to_dto(ride) for ride in data.rides],
        plan=plan_to_dto(data.plan) if data.plan is not None else None,
        help_requests=[_help_request_to_dto(request) for request in data.help_requests],
        deletion_requested_at=data.deletion_requested_at,
    )


def deletion_requests_to_dto(requests: list[OpenRequest]) -> DeletionRequestListDto:
    items = [
        DeletionRequestItemDto(
            user_id=request.user_id,
            role=request.role,  # type: ignore[arg-type]
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            requested_at=request.requested_at,
        )
        for request in requests
    ]
    return DeletionRequestListDto(items=items)


def _help_request_to_dto(request: SupportRequest) -> HelpRequestDto:
    return HelpRequestDto(
        kind=request.kind,  # type: ignore[arg-type]
        phone=request.phone,
        message=request.message,
        created_at=request.created_at,
        handled_at=request.handled_at,
    )
