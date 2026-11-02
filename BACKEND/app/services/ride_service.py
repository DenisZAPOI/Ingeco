"""
Booking a ride (UC10, UC11), its estimate (UC12), the simulated payment of
the rider's share (UC14), then its follow-up: lists (UC17), cancellation
(UC16) and rating (UC18).

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
from ..repository.ride_repository import (
    AlreadyRated,
    Contact,
    DriverInfo,
    DuplicateRequest,
    Position,
    Rating,
    Ride,
    Stop,
)
from ..utils import database
from ..utils.errors import Conflict, NotFound, ServiceUnavailable, UnprocessableEntity
from ..utils.locks import KeyedLock
from . import ride_rules
from .place_service import check_proposed, check_served, count_lookup
from .ride_rules import (
    APP_CHANNEL,
    AWAITING_PAYMENT,
    CANCELLED,
    COMPLETED,
    DRIVER_SEARCH_DELAY,
    EXPIRED,
    IN_PROGRESS,
    PAYMENT_DELAY,
    PAYMENT_PAID,
    PAYMENT_PENDING,
    PAYMENT_REFUNDED,
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
NOT_CANCELLABLE = "Ce trajet ne peut plus être annulé."
_NOT_CANCELLABLE = {
    IN_PROGRESS: "Le trajet a déjà commencé : il ne peut plus être annulé.",
    COMPLETED: "Ce trajet est terminé : il ne peut plus être annulé.",
    EXPIRED: "Ce trajet a expiré : il n'y a plus rien à annuler.",
}
NOT_FINISHED = "Vous pourrez noter ce trajet une fois arrivé."
ALREADY_RATED = "Vous avez déjà noté ce trajet. Merci !"
TOO_MANY_IMMEDIATE = (
    "Vous avez déjà un trajet en cours ou qui attend un chauffeur. "
    "Attendez qu'il soit terminé, ou annulez-le, avant d'en réserver un autre."
)
TOO_MANY_SCHEDULED = (
    f"Vous avez déjà {ride_rules.MAX_OPEN_SCHEDULED_RIDES} trajets programmés. "
    "Attendez que l'un d'eux soit passé, ou annulez-en un."
)

# Counting the open rides then inserting one: two bookings sent at the same
# moment must not both pass the count (audit F15).
rider_locks = KeyedLock()

# Who sees any ride (contract 4.2): the call centre and the administrators.
STAFF_ROLES = ("operator", "admin")


@dataclass(frozen=True)
class Estimate:
    distance_km: Decimal
    price_cents: int
    voucher_amount_cents: int
    rider_amount_cents: int


def estimate(pickup: Stop, dropoff: Stop, *, user_id: int) -> Estimate:
    """Distance and price, without saving anything."""
    count_lookup(user_id)
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
    with rider_locks.hold(rider_id), database.session() as session:
        already_booked = _replayed_booking(session, client_request_id, rider_id)
        if already_booked is not None:
            return already_booked, False
        _check_open_rides(session, rider_id, scheduled=scheduled_at is not None)

        rider = user_repository.find_by_id(session, rider_id)
        price = _estimate(session, pickup, dropoff)
        created_at = ride_rules.now()
        # The signatures were checked by _estimate: not stored with the ride.
        pickup, dropoff = _unsigned(pickup), _unsigned(dropoff)
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

    A driver also sees a ride waiting for a driver that they could take (an
    offer: online, with a fitting vehicle), without its rider's contact.
    Anyone else gets 404, as if it did not exist.
    """
    with database.session() as session:
        ride = ride_repository.find_by_id(session, ride_id)
        if ride is None or not _may_see(session, ride, user_id, role):
            raise NotFound(RIDE_NOT_FOUND)
        return present(session, [ride], user_id=user_id, role=role)[0]


def present(session: Session, rides: list[Ride], *, user_id: int, role: str) -> list[Ride]:
    """Adds to each ride what the caller may know of the other party.

    The rider (and the staff) see the driver: first name, vehicle, average
    rating, and their phone while the ride is under way. The driver sees the
    rider's first name and phone, only while the ride is under way: never on
    an offer.
    """
    driver_ids = {ride.driver_id for ride in rides if ride.driver_id is not None}
    rider_ids = {ride.rider_id for ride in rides}
    people = user_repository.find_by_ids(session, driver_ids | rider_ids)
    scores = ride_repository.average_scores(session, driver_ids)
    for ride in rides:
        under_way = ride.status in ride_rules.CONTACT_STATUSES
        staff = role in STAFF_ROLES
        if ride.driver_id is not None and (staff or user_id == ride.rider_id):
            driver = people[ride.driver_id]
            ride.driver = DriverInfo(
                id=driver.id,
                first_name=driver.first_name,
                phone=driver.phone if under_way or staff else None,
                vehicle_plate=driver.vehicle.plate,
                vehicle_model=driver.vehicle.model,
                vehicle_is_accessible=driver.vehicle.is_accessible,
                average_score=scores.get(driver.id),
            )
        if staff or (under_way and user_id == ride.driver_id):
            rider = people[ride.rider_id]
            ride.rider = Contact(first_name=rider.first_name, phone=rider.phone)
    return rides


def _may_see(session: Session, ride: Ride, user_id: int, role: str) -> bool:
    if role in STAFF_ROLES or user_id in (ride.rider_id, ride.driver_id):
        return True
    if role != "driver" or ride.status != PENDING:
        return False
    # The rules of the offers list (audit F10): an offline driver, or one whose
    # vehicle does not fit, cannot read the addresses of the rides waiting.
    driver = user_repository.find_by_id(session, user_id)
    fits = not ride.needs_accessible_vehicle or (driver.vehicle is not None and driver.vehicle.is_accessible)
    return driver.is_available and fits


@dataclass(frozen=True)
class RidePage:
    rides: list[Ride]
    # Where the next page starts; None on the last page.
    next_position: Position | None


def list_upcoming(*, user_id: int, role: str) -> list[Ride]:
    """The caller's rides not finished yet, the soonest first (UC17, "À venir")."""
    with database.session() as session:
        rides = ride_repository.find_upcoming(session, **_owner(user_id, role), statuses=ride_rules.UPCOMING_STATUSES)
        return present(session, rides, user_id=user_id, role=role)


def list_past(*, user_id: int, role: str, after: Position | None) -> RidePage:
    """A page of the caller's finished rides, the most recent first (UC17, "Passés")."""
    page_size = ride_rules.PAST_PAGE_SIZE
    with database.session() as session:
        # One more than the page: tells whether there is a next page, without counting.
        rides = ride_repository.find_page(
            session, **_owner(user_id, role), statuses=ride_rules.PAST_STATUSES, after=after, limit=page_size + 1
        )
        present(session, rides, user_id=user_id, role=role)
    if len(rides) <= page_size:
        return RidePage(rides=rides, next_position=None)
    last = rides[page_size - 1]
    return RidePage(rides=rides[:page_size], next_position=Position(created_at=last.created_at, ride_id=last.id))


def cancel_ride(*, user_id: int, role: str, ride_id: int) -> Ride:
    """Cancels a ride before the rider is on board (UC16, UC43).

    Refunds the paid share in full (H17, to confirm with the client).
    Cancelling a ride already cancelled returns it as it is: the button tapped
    twice on a slow network is not an error.
    """
    with database.session() as session:
        ride = ride_repository.find_by_id(session, ride_id)
        if ride is None or not (role in STAFF_ROLES or ride.rider_id == user_id):
            raise NotFound(RIDE_NOT_FOUND)
        if ride.status == CANCELLED:
            return present(session, [ride], user_id=user_id, role=role)[0]
        if ride.status not in ride_rules.CANCELLABLE_STATUSES:
            raise Conflict(_NOT_CANCELLABLE.get(ride.status, NOT_CANCELLABLE))

        if not cancel_in(session, ride, by_id=user_id):
            # Changed in between (driver started, other cancellation): answer with its new state.
            return present(session, [_cancellation_already_settled(session, ride_id)], user_id=user_id, role=role)[0]
        present(session, [ride], user_id=user_id, role=role)

    # No real-time yet (step 4): the driver, if any, sees it at their next reading.
    context = {"rideId": ride.id, "by": role, "hadDriver": ride.driver_id is not None}
    logger.info("Ride cancelled", extra={"context": context})
    return ride


def cancel_in(session: Session, ride: Ride, *, by_id: int) -> bool:
    """Cancels `ride`, read in `session`, and refunds its paid share. False if its status changed meanwhile.

    The write of cancel_ride, shared with the suspension of a rider (admin_service).
    """
    previous_status = ride.status
    ride.status = CANCELLED
    ride.cancelled_at = ride_rules.now()
    ride.cancelled_by_id = by_id
    if ride.payment_status == PAYMENT_PAID:
        # Simulated (H10): with a real provider, the refund call follows the transaction.
        ride.payment_status = PAYMENT_REFUNDED
    return ride_repository.update_if_status(session, ride, previous_status)


def rate_ride(*, rider_id: int, ride_id: int, score: int, comment: str | None) -> Ride:
    """The rider rates a finished ride, once (UC18)."""
    with database.session() as session:
        ride = ride_repository.find_by_id(session, ride_id)
        if ride is None or ride.rider_id != rider_id:
            raise NotFound(RIDE_NOT_FOUND)
        if ride.status != COMPLETED:
            raise Conflict(NOT_FINISHED)
        if ride.rating is not None:
            raise Conflict(ALREADY_RATED)
        rating = Rating(score=score, comment=comment, created_at=ride_rules.now())
        try:
            ride_repository.insert_rating(session, ride.id, rating)
        except AlreadyRated:
            # Two sendings at the same moment: the other one was saved.
            raise Conflict(ALREADY_RATED) from None
        ride.rating = rating
        present(session, [ride], user_id=rider_id, role="rider")

    logger.info("Ride rated", extra={"context": {"rideId": ride.id}})
    return ride


def _owner(user_id: int, role: str) -> dict[str, int | None]:
    """Whose rides: those booked by a rider, or those taken by a driver."""
    if role == "driver":
        return {"rider_id": None, "driver_id": user_id}
    return {"rider_id": user_id, "driver_id": None}


def _cancellation_already_settled(session: Session, ride_id: int) -> Ride:
    ride = ride_repository.find_by_id(session, ride_id)
    if ride.status == CANCELLED:
        return ride
    raise Conflict(_NOT_CANCELLABLE.get(ride.status, NOT_CANCELLABLE))


def _estimate(session: Session, pickup: Stop, dropoff: Stop) -> Estimate:
    for stop in (pickup, dropoff):
        check_proposed(stop.address, stop.lat, stop.lng, stop.commune_id, stop.token)
        check_served(session, stop.lat, stop.lng, stop.commune_id)

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


def _unsigned(stop: Stop) -> Stop:
    return Stop(address=stop.address, lat=stop.lat, lng=stop.lng, commune_id=stop.commune_id)


def _check_open_rides(session: Session, rider_id: int, *, scheduled: bool) -> None:
    """422 beyond 1 immediate ride and 3 scheduled ones not finished yet (audit F6)."""
    open_rides = ride_repository.find_upcoming(
        session, rider_id=rider_id, driver_id=None, statuses=ride_rules.UPCOMING_STATUSES
    )
    same_kind = [ride for ride in open_rides if (ride.scheduled_at is not None) == scheduled]
    if scheduled and len(same_kind) >= ride_rules.MAX_OPEN_SCHEDULED_RIDES:
        raise UnprocessableEntity(TOO_MANY_SCHEDULED)
    if not scheduled and len(same_kind) >= ride_rules.MAX_OPEN_IMMEDIATE_RIDES:
        raise UnprocessableEntity(TOO_MANY_IMMEDIATE)


def _replayed_booking(session: Session, client_request_id: str, rider_id: int) -> Ride | None:
    ride = ride_repository.find_by_client_request_id(session, client_request_id)
    if ride is not None and ride.rider_id != rider_id:
        raise Conflict(REQUEST_ID_TAKEN)
    return ride
