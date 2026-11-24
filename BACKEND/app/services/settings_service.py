"""
Settings of the administrator (cahier des charges §5 M9, P1): the service
hours, the served communes (zones) and the tariff.

Each change applies to NEW requests only (decided on 24/11/2026): a ride
already booked keeps its time, its communes and its price. Nothing is
cancelled automatically (no automated decision, RGPD art. 22).
"""

import logging
from dataclasses import dataclass
from datetime import time

from ..repository import commune_repository, service_hours_repository, tariff_repository
from ..repository.commune_repository import Commune
from ..repository.service_hours_repository import ServiceSlot
from ..repository.tariff_repository import Tariff
from ..utils import database
from ..utils.errors import UnprocessableEntity
from . import ride_rules, service_hours_rules

logger = logging.getLogger(__name__)

NO_OPEN_DAY = "Ouvrez le service au moins un jour : sinon, plus personne ne peut demander de trajet."
NO_SERVED_COMMUNE = "Gardez au moins une commune desservie : sinon, plus personne ne peut demander de trajet."
UNKNOWN_COMMUNE = "Une des communes choisies n'existe pas. Rechargez la page."


@dataclass(frozen=True)
class DayHours:
    """One day of the week on the screen: one slot, or closed (both None)."""

    # 1 = Monday … 7 = Sunday (ISO 8601)
    weekday: int
    opens_at: time | None
    closes_at: time | None

    @property
    def is_open(self) -> bool:
        return self.opens_at is not None


# --- Service hours -----------------------------------------------------------

def get_week() -> list[DayHours]:
    """The 7 days, Monday first, as the screen shows them: one slot per day.

    The screen offers one slot per day (decided on 24/11/2026). If the table
    holds several for a day (written by hand), the day is shown from its first
    opening to its last closing, and saving the screen keeps only that slot.
    """
    with database.session() as session:
        slots = service_hours_repository.list_slots(session)
    return [_day_from_slots(weekday, slots) for weekday in service_hours_rules.WEEKDAYS]


def save_week(*, admin_id: int, days: list[DayHours]) -> list[DayHours]:
    """Replaces the hours of the whole week. `days`: the 7 days, checked by the DTO."""
    open_days = [day for day in days if day.is_open]
    if not open_days:
        raise UnprocessableEntity(NO_OPEN_DAY)
    slots = [ServiceSlot(day.weekday, day.opens_at, day.closes_at) for day in open_days]
    with database.session() as session:
        service_hours_repository.replace_week(session, slots)
    logger.info("Service hours changed", extra={"context": {"openDays": len(open_days), "byAdminId": admin_id}})
    return get_week()


def _day_from_slots(weekday: int, slots: list[ServiceSlot]) -> DayHours:
    day_slots = [slot for slot in slots if slot.weekday == weekday]
    if not day_slots:
        return DayHours(weekday=weekday, opens_at=None, closes_at=None)
    first_opening = min(slot.opens_at for slot in day_slots)
    last_closing = max(slot.closes_at for slot in day_slots)
    return DayHours(weekday=weekday, opens_at=first_opening, closes_at=last_closing)


# --- Zones -------------------------------------------------------------------

def list_zones() -> list[Commune]:
    """The 22 communes, by name, served or not."""
    with database.session() as session:
        return commune_repository.list_communes(session, served_only=False)


def save_zones(*, admin_id: int, served_ids: set[int]) -> list[Commune]:
    """These communes receive rides from now on, the others no longer do."""
    if not served_ids:
        raise UnprocessableEntity(NO_SERVED_COMMUNE)
    with database.session() as session:
        known_ids = {commune.id for commune in commune_repository.list_communes(session, served_only=False)}
        if not served_ids <= known_ids:
            raise UnprocessableEntity(UNKNOWN_COMMUNE)
        commune_repository.set_served(session, served_ids)
        communes = commune_repository.list_communes(session, served_only=False)
    logger.info("Zones changed", extra={"context": {"servedCommunes": len(served_ids), "byAdminId": admin_id}})
    return communes


# --- Tariff ------------------------------------------------------------------

def get_tariff() -> Tariff:
    with database.session() as session:
        return tariff_repository.active_tariff(session)


def new_tariff(*, admin_id: int, base_fare_cents: int, per_km_cents: int) -> Tariff:
    """A new version of the tariff, for the next bookings. Amounts checked by the DTO."""
    with database.session() as session:
        tariff = tariff_repository.new_version(
            session,
            base_fare_cents=base_fare_cents,
            per_km_cents=per_km_cents,
            created_at=ride_rules.now(),
        )
    logger.info("Tariff changed", extra={"context": {"tariffId": tariff.id, "byAdminId": admin_id}})
    return tariff
