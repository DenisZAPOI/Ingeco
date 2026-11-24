"""
Service hours: when a ride can be requested (table `horaire_service` of the DB
team, migration 018), set by the administrator (cahier des charges §5 M9).

Times are in LOCAL time of Cayenne, unlike every DATETIME of the schema: the
caller converts the time of the ride before comparing (service_hours_rules).
"""

from dataclasses import dataclass
from datetime import time

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..models import ServiceHoursRow


@dataclass(frozen=True)
class ServiceSlot:
    # 1 = Monday … 7 = Sunday (ISO 8601)
    weekday: int
    opens_at: time
    closes_at: time


def list_slots(session: Session) -> list[ServiceSlot]:
    """Every slot of the week, by day then by opening time. No slot for a day: closed that day."""
    query = select(ServiceHoursRow).order_by(ServiceHoursRow.weekday, ServiceHoursRow.opens_at)
    return [_to_slot(row) for row in session.scalars(query)]


def replace_week(session: Session, slots: list[ServiceSlot]) -> None:
    """The whole week at once: the old slots are removed, these written.

    Rides already booked are not touched: the hours only apply to new requests.
    """
    session.execute(delete(ServiceHoursRow))
    for slot in slots:
        session.add(ServiceHoursRow(weekday=slot.weekday, opens_at=slot.opens_at, closes_at=slot.closes_at))
    session.flush()


def _to_slot(row: ServiceHoursRow) -> ServiceSlot:
    return ServiceSlot(weekday=row.weekday, opens_at=row.opens_at, closes_at=row.closes_at)
