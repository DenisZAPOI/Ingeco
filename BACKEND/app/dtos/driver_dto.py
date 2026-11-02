"""Bodies, queries and responses of /drivers/me."""

from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from ..services import ride_rules
from ..services.driver_service import Earnings, Offer, Offers
from .base import ApiModel, InputModel, field_error
from .ride_dto import RideDto, ride_to_dto


class AvailabilityBody(InputModel):
    is_available: bool


class AvailabilityDto(ApiModel):
    is_available: bool


class LocationBody(InputModel):
    lat: float = Field(ge=-90, le=90, examples=[4.9372])
    lng: float = Field(ge=-180, le=180, examples=[-52.326])


class OffersQuery(InputModel):
    # immediate: leave now, near the driver. scheduled: booked ahead, by date.
    type: Literal["immediate", "scheduled"]


class OfferDto(ApiModel):
    ride: RideDto
    # Straight-line distance to the pickup; null for scheduled rides, or without a recent position.
    distance_to_pickup_km: float | None = Field(examples=[2.4])


class OfferListDto(ApiModel):
    items: list[OfferDto]
    # false: no recent position, so the whole zone, without distance.
    located: bool


def offers_to_dto(offers: Offers) -> OfferListDto:
    return OfferListDto(items=[_offer_to_dto(offer) for offer in offers.offers], located=offers.located)


# Shown rounded to 100 m, like the distance of a ride.
_DISTANCE_DECIMALS = 1


def _offer_to_dto(offer: Offer) -> OfferDto:
    distance = offer.distance_to_pickup_km
    return OfferDto(
        ride=ride_to_dto(offer.ride),
        distance_to_pickup_km=round(distance, _DISTANCE_DECIMALS) if distance is not None else None,
    )


# --- Earnings (UC28) ---------------------------------------------------------

class EarningsQuery(InputModel):
    """Days in Guyana time, both included: ?from=2026-11-02&to=2026-11-08. A month at most."""

    first_day: date = Field(alias="from", examples=["2026-11-02"])
    last_day: date = Field(alias="to", examples=["2026-11-08"])

    @model_validator(mode="after")
    def _period(self) -> "EarningsQuery":
        try:
            ride_rules.check_earnings_period(self.first_day, self.last_day)
        except ValueError as error:
            raise field_error(str(error)) from None
        return self


class DayEarningsDto(ApiModel):
    # A day in Guyana time.
    day: date = Field(examples=["2026-11-02"])
    ride_count: int
    total_cents: int


class EarningsDto(ApiModel):
    total_cents: int = Field(examples=[5544])
    ride_count: int
    # Only the days with a completed ride, the most recent first.
    days: list[DayEarningsDto]


def earnings_to_dto(earnings: Earnings) -> EarningsDto:
    return EarningsDto(
        total_cents=earnings.total_cents,
        ride_count=earnings.ride_count,
        days=[
            DayEarningsDto(day=day.day, ride_count=day.ride_count, total_cents=day.total_cents)
            for day in earnings.days
        ],
    )
