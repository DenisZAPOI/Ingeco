"""The driver's own state: online or offline, position, rides offered."""

from flask import Blueprint, jsonify, request
from flask_pydantic_spec import Response

from ..dtos.base import ErrorDto
from ..dtos.driver_dto import (
    AvailabilityBody,
    AvailabilityDto,
    EarningsDto,
    EarningsQuery,
    LocationBody,
    OfferListDto,
    OffersQuery,
    earnings_to_dto,
    offers_to_dto,
)
from ..extensions import spec
from ..services import driver_service
from ..utils.access import current_user_id, require_login

driver_bp = Blueprint("drivers", __name__, url_prefix="/drivers")

_TAGS = ["Chauffeur"]


@driver_bp.put("/me/availability")
@require_login("driver")
@spec.validate(
    body=AvailabilityBody,
    resp=Response(HTTP_200=AvailabilityDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto),
    tags=_TAGS,
)
def set_availability():
    """Online or offline. Offline erases the last position; the rides already accepted are kept."""
    body: AvailabilityBody = request.context.body
    driver_service.set_availability(current_user_id(), body.is_available)
    return jsonify(AvailabilityDto(is_available=body.is_available).to_json()), 200


@driver_bp.put("/me/location")
@require_login("driver")
@spec.validate(
    body=LocationBody,
    resp=Response(HTTP_204=None, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_409=ErrorDto),
    tags=_TAGS,
)
def set_location():
    """Last position of an online driver, sent by their phone. Only the last one is kept. 409 if offline."""
    body: LocationBody = request.context.body
    driver_service.set_location(current_user_id(), body.lat, body.lng)
    return "", 204


@driver_bp.get("/me/ride-offers")
@require_login("driver")
@spec.validate(
    query=OffersQuery,
    resp=Response(HTTP_200=OfferListDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_409=ErrorDto),
    tags=_TAGS,
)
def list_offers():
    """Rides waiting for a driver that fit their vehicle. 409 if offline.

    type=immediate: within 10 km of the driver, the nearest first (the whole
    zone if their position is unknown or older than 5 minutes: located=false).
    type=scheduled: all of them, by date.
    """
    query: OffersQuery = request.context.query
    offers = driver_service.list_offers(current_user_id(), scheduled=query.type == "scheduled")
    return jsonify(offers_to_dto(offers).to_json()), 200


@driver_bp.get("/me/earnings")
@require_login("driver")
@spec.validate(
    query=EarningsQuery,
    resp=Response(HTTP_200=EarningsDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto),
    tags=_TAGS,
)
def earnings():
    """Total and number of completed rides from `from` to `to` (Guyana days, both included), per day.

    A ride counts on the day it was completed, for its whole price (no
    commission, H9). Only the days with a ride, the most recent first. A month at most.
    """
    query: EarningsQuery = request.context.query
    result = driver_service.earnings(current_user_id(), query.first_day, query.last_day)
    return jsonify(earnings_to_dto(result).to_json()), 200
