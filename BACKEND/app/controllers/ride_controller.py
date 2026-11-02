"""Booking a ride, its estimate, its simulated payment and its detail."""

from flask import Blueprint, jsonify, request
from flask_pydantic_spec import Response

from ..dtos.base import ErrorDto
from ..dtos.ride_dto import BookRideBody, EstimateBody, EstimateDto, RideDto, estimate_to_dto, ride_to_dto
from ..extensions import spec
from ..services import ride_service
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
