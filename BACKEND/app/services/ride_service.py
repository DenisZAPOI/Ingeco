"""
Booking a ride (UC10, UC11), its estimate (UC12) and the simulated payment of
the rider's share (UC14).

The price is always computed here, from the active tariff and the road
distance: the price shown by the estimate is never taken back as is.

Vouchers are not in the MVP schema yet (their rules are not set by the
client): the rider pays the whole price, so every ride starts awaiting
payment.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from ..repository import ride_repository, tariff_repository, user_repository
from ..repository.place_repository import PlacesUnavailable, road_distance_km
from ..repository.ride_repository import DuplicateRequest, Ride, Stop
from ..utils import database
from ..utils.errors import Conflict, NotFound, ServiceUnavailable, UnprocessableEntity
from . import ride_rules
from .place_service import check_served
from .ride_rules import (
    APP_CHANNEL,
    AWAITING_PAYMENT,
    DRIVER_SEARCH_DELAY,
    PAYMENT_DELAY,
    PAYMENT_PAID,
    PAYMENT_PENDING,
    PENDING,
)

logger = logging.getLogger(__name__)

# Below 100 m, pickup and drop-off are the same place for the user.
MIN_DISTANCE_KM = Decimal("0.1")

SAME_PLACE = "Le départ et l'arrivée sont au même endroit. Choisissez une autre adresse d'arrivée."
RIDE_NOT_FOUND = "Ce trajet est introuvable."
REQUEST_ID_TAKEN = "Cette réservation a déjà été envoyée depuis un autre compte. Recommencez la réservation."
DISTANCE_UNAVAILABLE = "Le calcul du trajet ne répond pas pour le moment. Réessayez dans quelques minutes."
PAYMENT_TOO_LATE = "Le délai de paiement de 15 minutes est dépassé. Refaites la réservation."
NOT_AWAITING_PAYMENT = "Ce trajet n'attend pas de paiement."

# Who sees any ride (contract 4.2): the call centre and the administrators.
STAFF_ROLES = ("operator", "admin")


@dataclass(frozen=True)
class Estimate:
    distance_km: Decimal
    price_cents: int
    voucher_amount_cents: int
    rider_amount_cents: int


def estimate(pickup: Stop, dropoff: Stop) -> Estimate:
    """Distance and price, without saving anything."""
    with database.session() as session:
        return _estimate(session, pickup, dropoff)


def book_ride(
    *,
    rider_id: int,
    client_request_id: str,
    purpose: str,
    pickup: Stop,
    dropoff: Stop,
    scheduled_at: datetime | None,
) -> tuple[Ride, bool]:
    """Books a ride for the logged-in rider. Returns (ride, created).

    Sent again with the same client_request_id (network cut during the
    sending), it returns the ride already booked instead of a second one.
    """
    with database.session() as session:
        already_booked = _replayed_booking(session, client_request_id, rider_id)
        if already_booked is not None:
            return already_booked, False

        rider = user_repository.find_by_id(session, rider_id)
        price = _estimate(session, pickup, dropoff)
        created_at = ride_rules.now()
        ride = Ride(
            client_request_id=client_request_id,
            rider_id=rider_id,
            booked_by_id=rider_id,
            channel=APP_CHANNEL,
            status=AWAITING_PAYMENT,
            purpose=purpose,
            pickup=pickup,
            dropoff=dropoff,
            scheduled_at=scheduled_at,
            needs_accessible_vehicle=rider.needs_accessible_vehicle,
            distance_km=price.distance_km,
            tariff_id=tariff_repository.active_tariff(session).id,
            price_cents=price.price_cents,
            payment_status=PAYMENT_PENDING,
            expires_at=created_at + PAYMENT_DELAY,
            created_at=created_at,
        )
        try:
            ride = ride_repository.insert_ride(session, ride)
        except DuplicateRequest:
            # Two sendings of the same booking at the same moment: the other one won.
            return _replayed_booking(session, client_request_id, rider_id), False

    logger.info("Ride booked", extra={"context": {"rideId": ride.id, "scheduled": scheduled_at is not None}})
    return ride, True


def pay_ride(*, rider_id: int, ride_id: int) -> Ride:
    """Simulated card payment of the rider's share (H10).

    The ride then waits for a driver. Paying again a paid ride returns it as
    it is: the button tapped twice on a slow network is not an error.
    """
    with database.session() as session:
        ride = ride_repository.find_by_id(session, ride_id)
        if ride is None or ride.rider_id != rider_id:
            raise NotFound(RIDE_NOT_FOUND)
        if ride.payment_status == PAYMENT_PAID:
            return ride
        if ride.status != AWAITING_PAYMENT:
            raise Conflict(NOT_AWAITING_PAYMENT)

        paid_at = ride_rules.now()
        if paid_at >= ride.expires_at:
            raise Conflict(PAYMENT_TOO_LATE)

        ride.status = PENDING
        ride.payment_status = PAYMENT_PAID
        ride.paid_at = paid_at
        # A scheduled ride waits for a driver until its time; an immediate one, 15 minutes.
        ride.expires_at = ride.scheduled_at or paid_at + DRIVER_SEARCH_DELAY
        if not ride_repository.update_if_status(session, ride, AWAITING_PAYMENT):
            # Changed in between (other payment, cancellation): answer with its new state.
            return _payment_already_settled(session, ride_id)

    logger.info("Ride paid", extra={"context": {"rideId": ride.id}})
    return ride


def _payment_already_settled(session: Session, ride_id: int) -> Ride:
    """The ride after a payment that lost the race: paid by the other one, or no longer payable."""
    ride = ride_repository.find_by_id(session, ride_id)
    if ride.payment_status == PAYMENT_PAID:
        return ride
    raise Conflict(NOT_AWAITING_PAYMENT)


def get_ride(*, user_id: int, role: str, ride_id: int) -> Ride:
    """A ride, for its rider, its driver, the call centre or an administrator.

    Anyone else gets 404, as if it did not exist.
    """
    with database.session() as session:
        ride = ride_repository.find_by_id(session, ride_id)
    if ride is None or not (role in STAFF_ROLES or user_id in (ride.rider_id, ride.driver_id)):
        raise NotFound(RIDE_NOT_FOUND)
    return ride


def _estimate(session: Session, pickup: Stop, dropoff: Stop) -> Estimate:
    check_served(session, pickup.lat, pickup.lng, pickup.commune_id)
    check_served(session, dropoff.lat, dropoff.lng, dropoff.commune_id)

    try:
        road_km = road_distance_km(pickup.lat, pickup.lng, dropoff.lat, dropoff.lng)
    except PlacesUnavailable:
        # No price without a real distance (decided with the team): better to
        # ask to retry than to charge a wrong amount.
        raise ServiceUnavailable(DISTANCE_UNAVAILABLE) from None
    distance_km = ride_rules.round_distance(road_km)
    if distance_km < MIN_DISTANCE_KM:
        raise UnprocessableEntity(SAME_PLACE)

    tariff = tariff_repository.active_tariff(session)
    price = ride_rules.price_cents(tariff.base_fare_cents, tariff.per_km_cents, distance_km)
    # No voucher yet: the rider's share is the whole price.
    return Estimate(distance_km=distance_km, price_cents=price, voucher_amount_cents=0, rider_amount_cents=price)


def _replayed_booking(session: Session, client_request_id: str, rider_id: int) -> Ride | None:
    ride = ride_repository.find_by_client_request_id(session, client_request_id)
    if ride is not None and ride.rider_id != rider_id:
        raise Conflict(REQUEST_ID_TAKEN)
    return ride
