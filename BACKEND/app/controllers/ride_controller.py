"""Booking a ride, its estimate, its simulated payment, its detail, then lists, cancellation and rating."""

from flask import Blueprint, jsonify, request
from flask_pydantic_spec import Response

from ..dtos.base import ErrorDto
from ..dtos.ride_dto import (
    BookRideBody,
    EstimateBody,
    EstimateDto,
    RateRideBody,
    RideDto,
    RideListDto,
    RideListQuery,
    estimate_to_dto,
    ride_list_to_dto,
    ride_page_to_dto,
    ride_to_dto,
)
from ..extensions import spec
from ..services import driver_service, ride_service
from ..utils.access import current_role, current_user_id, require_login

ride_bp = Blueprint("rides", __name__, url_prefix="/rides")

_TAGS = ["Réservation"]


@ride_bp.post("/estimate")
@require_login("rider", "operator", "admin")
@spec.validate(
    body=EstimateBody,
    resp=Response(
        HTTP_200=EstimateDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_422=ErrorDto, HTTP_503=ErrorDto
    ),
    tags=_TAGS,
)
def estimate():
    """Road distance and price of a trip. Saves nothing.

    422 if the pickup or the drop-off is outside the served zone, 503 if the
    road distance cannot be computed.
    """
    body: EstimateBody = request.context.body
    return jsonify(estimate_to_dto(ride_service.estimate(body.pickup.to_stop(), body.dropoff.to_stop())).to_json()), 200


@ride_bp.post("")
@require_login("rider")
@spec.validate(
    body=BookRideBody,
    resp=Response(
        HTTP_200=RideDto,
        HTTP_201=RideDto,
        HTTP_400=ErrorDto,
        HTTP_401=ErrorDto,
        HTTP_403=ErrorDto,
        HTTP_409=ErrorDto,
        HTTP_422=ErrorDto,
        HTTP_503=ErrorDto,
    ),
    tags=_TAGS,
)
def book():
    """Books an immediate or scheduled ride. It waits for the rider's payment.

    The price is computed again here, never taken from the estimate. Sent again
    with the same clientRequestId, it returns the ride already booked (200)
    instead of booking a second one (201).
    """
    body: BookRideBody = request.context.body
    ride, created = ride_service.book_ride(
        rider_id=current_user_id(),
        client_request_id=str(body.client_request_id),
        purpose=body.purpose,
        pickup=body.pickup.to_stop(),
        dropoff=body.dropoff.to_stop(),
        scheduled_at=body.scheduled_at,
    )
    return jsonify(ride_to_dto(ride).to_json()), 201 if created else 200


@ride_bp.get("")
@require_login("rider", "driver")
@spec.validate(
    query=RideListQuery,
    resp=Response(HTTP_200=RideListDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto),
    tags=_TAGS,
)
def list_rides():
    """The caller's rides: booked by a rider, or taken by a driver.

    when=upcoming: not finished yet, all of them, the soonest first.
    when=past: finished, cancelled or expired, the most recent first, 20 per
    page; send nextCursor back as cursor for the next page.
    """
    query: RideListQuery = request.context.query
    user_id, role = current_user_id(), current_role()
    if query.when == "upcoming":
        dto = ride_list_to_dto(ride_service.list_upcoming(user_id=user_id, role=role))
    else:
        dto = ride_page_to_dto(ride_service.list_past(user_id=user_id, role=role, after=query.position()))
    return jsonify(dto.to_json()), 200


@ride_bp.get("/<int:ride_id>")
@require_login()
@spec.validate(resp=Response(HTTP_200=RideDto, HTTP_401=ErrorDto, HTTP_404=ErrorDto), tags=_TAGS)
def get(ride_id: int):
    """A ride, for its rider, its driver, the call centre or an administrator. 404 for anyone else."""
    ride = ride_service.get_ride(user_id=current_user_id(), role=current_role(), ride_id=ride_id)
    return jsonify(ride_to_dto(ride).to_json()), 200


@ride_bp.post("/<int:ride_id>/payment")
@require_login("rider")
@spec.validate(
    resp=Response(HTTP_200=RideDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto, HTTP_409=ErrorDto),
    tags=_TAGS,
)
def pay(ride_id: int):
    """Simulated payment of the rider's share: the ride then waits for a driver.

    Paying a ride already paid returns it as it is. 409 once the 15 minutes
    to pay are over, or if the ride no longer awaits payment.
    """
    return jsonify(ride_to_dto(ride_service.pay_ride(rider_id=current_user_id(), ride_id=ride_id)).to_json()), 200


@ride_bp.post("/<int:ride_id>/cancel")
@require_login("rider", "operator", "admin")
@spec.validate(
    resp=Response(HTTP_200=RideDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto, HTTP_409=ErrorDto),
    tags=_TAGS,
)
def cancel(ride_id: int):
    """Cancels a ride before the rider is on board, and refunds its paid share in full.

    By its rider, the call centre or an administrator. Cancelling it again
    returns it as it is. 409 once the ride has started, is over or expired.
    """
    ride = ride_service.cancel_ride(user_id=current_user_id(), role=current_role(), ride_id=ride_id)
    return jsonify(ride_to_dto(ride).to_json()), 200


@ride_bp.post("/<int:ride_id>/rating")
@require_login("rider")
@spec.validate(
    body=RateRideBody,
    resp=Response(
        HTTP_201=RideDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto, HTTP_409=ErrorDto
    ),
    tags=_TAGS,
)
def rate(ride_id: int):
    """The rider rates a finished ride: a score from 1 to 5, an optional comment.

    Returns the ride with its rating. 409 if it is not finished, or already rated.
    """
    body: RateRideBody = request.context.body
    ride = ride_service.rate_ride(rider_id=current_user_id(), ride_id=ride_id, score=body.score, comment=body.comment)
    return jsonify(ride_to_dto(ride).to_json()), 201


@ride_bp.post("/<int:ride_id>/accept")
@require_login("driver")
@spec.validate(
    resp=Response(HTTP_200=RideDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto, HTTP_409=ErrorDto),
    tags=["Chauffeur"],
)
def accept(ride_id: int):
    """Takes a ride waiting for a driver, if online. Accepting again returns it.

    409 if already taken, no longer offered, needing an accessible vehicle,
    or less than an hour from a ride the driver already holds.
    """
    return jsonify(ride_to_dto(driver_service.accept_ride(current_user_id(), ride_id)).to_json()), 200


@ride_bp.post("/<int:ride_id>/release")
@require_login("driver")
@spec.validate(
    resp=Response(HTTP_200=RideDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto, HTTP_409=ErrorDto),
    tags=["Chauffeur"],
)
def release(ride_id: int):
    """The driver gives up a ride not started yet.

    It is offered again to the other drivers; the rider pays nothing more.
    """
    return jsonify(ride_to_dto(driver_service.release_ride(current_user_id(), ride_id)).to_json()), 200


@ride_bp.post("/<int:ride_id>/start")
@require_login("driver")
@spec.validate(
    resp=Response(HTTP_200=RideDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto, HTTP_409=ErrorDto),
    tags=["Chauffeur"],
)
def start(ride_id: int):
    """The rider is on board. Starting again returns it.

    A scheduled ride starts at the earliest one hour before its time.
    """
    return jsonify(ride_to_dto(driver_service.start_ride(current_user_id(), ride_id)).to_json()), 200


@ride_bp.post("/<int:ride_id>/complete")
@require_login("driver")
@spec.validate(
    resp=Response(HTTP_200=RideDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto, HTTP_409=ErrorDto),
    tags=["Chauffeur"],
)
def complete(ride_id: int):
    """Arrived: the rider is asked to rate the ride. Completing again returns it."""
    return jsonify(ride_to_dto(driver_service.complete_ride(current_user_id(), ride_id)).to_json()), 200
