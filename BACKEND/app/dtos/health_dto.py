"""Response of GET /health."""

from typing import Literal

from ..services.health_service import DatabaseState
from .base import ApiModel


class DatabaseStateDto(ApiModel):
    reachable: bool
    dialect: str | None = None


class HealthDto(ApiModel):
    status: Literal["ok", "degraded"]
    database: DatabaseStateDto


def health_to_dto(state: DatabaseState) -> HealthDto:
    return HealthDto(status="ok", database=DatabaseStateDto(reachable=True, dialect=state.dialect))


def degraded_health_dto() -> HealthDto:
    """No technical detail: it is in the logs, never in the response."""
    return HealthDto(status="degraded", database=DatabaseStateDto(reachable=False))
