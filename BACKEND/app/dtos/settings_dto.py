"""Bodies and responses of the administrator's settings: /admin/service-hours, /admin/zones, /admin/tariff."""

from datetime import datetime, time

from pydantic import Field, model_validator

from ..repository.commune_repository import Commune
from ..repository.tariff_repository import Tariff
from ..services import service_hours_rules
from ..services.settings_service import DayHours
from .base import ApiModel, InputModel, field_error

DAYS_IN_WEEK = len(service_hours_rules.WEEKDAYS)
FIRST_WEEKDAY = min(service_hours_rules.WEEKDAYS)
LAST_WEEKDAY = max(service_hours_rules.WEEKDAYS)

# Far above any real fare: catches a typing slip (800 € instead of 8 €).
MAX_BASE_FARE_CENTS = 100_00
MAX_PER_KM_CENTS = 10_00

HALF_DAY = "Indiquez l'heure d'ouverture et l'heure de fermeture, ou choisissez « Fermé »."
CLOSES_BEFORE_OPENING = "L'heure de fermeture doit être après l'heure d'ouverture."
NOT_A_WEEK = "Donnez les horaires des 7 jours de la semaine, une fois chacun."


# --- Service hours -----------------------------------------------------------

class DayHoursBody(InputModel):
    # 1 = Monday … 7 = Sunday (ISO 8601)
    weekday: int = Field(ge=FIRST_WEEKDAY, le=LAST_WEEKDAY, examples=[1])
    # Local time of Cayenne, "06:00". Both null: closed that day.
    opens_at: time | None = Field(examples=["06:00"])
    # 23:59 means until midnight.
    closes_at: time | None = Field(examples=["20:00"])

    @model_validator(mode="after")
    def _one_slot_or_closed(self) -> "DayHoursBody":
        is_closed = self.opens_at is None and self.closes_at is None
        if is_closed:
            return self
        has_both_times = self.opens_at is not None and self.closes_at is not None
        if not has_both_times:
            raise field_error(HALF_DAY)
        self.closes_at = service_hours_rules.stored_closing(self.closes_at)
        if self.closes_at <= self.opens_at:
            raise field_error(CLOSES_BEFORE_OPENING)
        return self

    def to_day(self) -> DayHours:
        return DayHours(weekday=self.weekday, opens_at=self.opens_at, closes_at=self.closes_at)


class WeekBody(InputModel):
    """The whole week at once, saved by one button."""

    days: list[DayHoursBody]

    @model_validator(mode="after")
    def _seven_days(self) -> "WeekBody":
        weekdays = {day.weekday for day in self.days}
        has_each_day_once = len(self.days) == DAYS_IN_WEEK and len(weekdays) == DAYS_IN_WEEK
        if not has_each_day_once:
            raise field_error(NOT_A_WEEK)
        return self

    def to_days(self) -> list[DayHours]:
        return [day.to_day() for day in self.days]


class DayHoursDto(ApiModel):
    weekday: int
    # null: closed that day. 23:59:59: until midnight.
    opens_at: time | None
    closes_at: time | None


class WeekDto(ApiModel):
    # Monday first.
    days: list[DayHoursDto]


def week_to_dto(days: list[DayHours]) -> WeekDto:
    items = [DayHoursDto(weekday=day.weekday, opens_at=day.opens_at, closes_at=day.closes_at) for day in days]
    return WeekDto(days=items)


# --- Zones -------------------------------------------------------------------

class ZonesBody(InputModel):
    """The communes that receive rides; every other one stops."""

    served_commune_ids: list[int] = Field(examples=[[1, 2, 3]])


class ZoneDto(ApiModel):
    id: int
    name: str
    is_served: bool


class ZoneListDto(ApiModel):
    # By name, served or not.
    items: list[ZoneDto]


def zones_to_dto(communes: list[Commune]) -> ZoneListDto:
    items = [ZoneDto(id=commune.id, name=commune.name, is_served=commune.served) for commune in communes]
    return ZoneListDto(items=items)


# --- Tariff ------------------------------------------------------------------

class TariffBody(InputModel):
    """A new version of the tariff, in cents: 800 for 8 €."""

    base_fare_cents: int = Field(ge=0, le=MAX_BASE_FARE_CENTS, examples=[800])
    per_km_cents: int = Field(ge=0, le=MAX_PER_KM_CENTS, examples=[80])


class TariffDto(ApiModel):
    id: int
    base_fare_cents: int
    per_km_cents: int
    # Since when it applies to new bookings.
    created_at: datetime


def tariff_to_dto(tariff: Tariff) -> TariffDto:
    return TariffDto(
        id=tariff.id,
        base_fare_cents=tariff.base_fare_cents,
        per_km_cents=tariff.per_km_cents,
        created_at=tariff.created_at,
    )
