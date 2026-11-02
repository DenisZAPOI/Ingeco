"""Bodies, queries and responses of /drivers/me."""

from typing import Literal

from pydantic import Field

from ..services.driver_service import Offer, Offers
from .base import ApiModel, InputModel
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
