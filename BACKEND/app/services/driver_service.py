"""
The driver side: online or offline (UC20), position (UC21), rides offered
(UC22), then accept (UC23), release (UC24), start (UC26) and complete (UC27).

Every change of a ride is a conditional write on its expected status
(contract 6.2): of two drivers accepting at the same moment, one wins.
"""

import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from ..repository import ride_repository, user_repository
from ..repository.place_repository import straight_distance_km
from ..repository.ride_repository import Ride
from ..repository.user_repository import Location, User
from ..utils import database
from ..utils.errors import Conflict, Forbidden, NotFound
from . import ride_rules
from .account_rules import DRIVER, SUSPENDED
from .auth_service import ACCOUNT_SUSPENDED
from .ride_rules import ACCEPTED, COMPLETED, IN_PROGRESS, PENDING
from .ride_service import RIDE_NOT_FOUND, present

logger = logging.getLogger(__name__)


OFFLINE = "Vous êtes hors ligne. Appuyez sur « Je suis disponible » pour voir les courses."
ALREADY_TAKEN = "Course déjà prise par un autre chauffeur."
NO_LONGER_OFFERED = "Cette course n'est plus proposée : elle a été annulée ou a expiré."
NEEDS_ACCESSIBLE_VEHICLE = "Cette course demande un véhicule adapté (fauteuil roulant)."
TIMETABLE_CLASH = (
    "Vous avez déjà une course en cours ou prévue à moins d'une heure de celle-ci. "
    "Terminez-la ou choisissez une autre course."
)
NOT_YOUR_RIDE = "Vous n'êtes plus le chauffeur de cette course."
NOT_ACCEPTED = "Cette course n'est pas en attente de départ."
TOO_EARLY = "Cette course est programmée plus tard : vous pourrez la démarrer une heure avant."
NOT_IN_PROGRESS = "Cette course n'a pas encore démarré."


@dataclass(frozen=True)
class Offer:
    ride: Ride
    # Straight-line distance from the driver to the pickup; None without a recent position.
    distance_to_pickup_km: float | None


@dataclass(frozen=True)
class Offers:
    offers: list[Offer]
    # False: no recent position, so the immediate rides of the whole zone, without distance.
    located: bool


# --- Online, position --------------------------------------------------------

def set_availability(driver_id: int, available: bool) -> None:
    """Online or offline. Offline erases the position; the rides held are kept."""
    with database.session() as session:
        # A suspended driver keeps a valid token for up to 15 minutes: it
        # must not be enough to come back online.
        if available and user_repository.find_by_id(session, driver_id).status == SUSPENDED:
            raise Forbidden(ACCOUNT_SUSPENDED)
        user_repository.set_availability(session, driver_id, available)
    logger.info("Driver availability", extra={"context": {"driverId": driver_id, "available": available}})


def set_location(driver_id: int, lat: float, lng: float) -> None:
    """Keeps the driver's last position. Never logged (GDPR)."""
    with database.session() as session:
        if not user_repository.set_location(session, driver_id, Location(lat=lat, lng=lng, at=ride_rules.now())):
            raise Conflict(OFFLINE)


# --- Offers ------------------------------------------------------------------

def list_offers(driver_id: int, *, scheduled: bool) -> Offers:
    """Rides the driver could take, if online.

    Immediate ones: within 10 km of their position, the nearest first; the
    whole zone, oldest first, without a recent position. Scheduled ones: all
    of them, by date (the position of today says nothing of next week).
    """
    with database.session() as session:
        driver = _online_driver(session, driver_id)
        rides = ride_repository.find_pending(session, scheduled=scheduled, accessible_vehicle=_accessible(driver))
        # The expiry task does not exist yet (UC60): a ride past its time is not offered.
        now = ride_rules.now()
        rides = [ride for ride in rides if ride.expires_at > now]
        present(session, rides, user_id=driver_id, role=DRIVER)

    position = _recent_position(driver)
    if scheduled or position is None:
        without_distance = [Offer(ride=ride, distance_to_pickup_km=None) for ride in rides]
        return Offers(offers=without_distance, located=position is not None)

    offers = [Offer(ride=ride, distance_to_pickup_km=_distance(position, ride)) for ride in rides]
    nearby = [offer for offer in offers if offer.distance_to_pickup_km <= ride_rules.OFFER_RADIUS_KM]
    nearby.sort(key=lambda offer: offer.distance_to_pickup_km)
    return Offers(offers=nearby, located=True)


# --- A ride ------------------------------------------------------------------

def accept_ride(driver_id: int, ride_id: int) -> Ride:
    """Takes a ride waiting for a driver. Accepting again a ride already taken by the same driver returns it."""
    with database.session() as session:
        driver = _online_driver(session, driver_id)
        ride = _find(session, ride_id)
        if ride.driver_id == driver_id and ride.status in ride_rules.HELD_STATUSES:
            return _present(session, ride, driver_id)
        _check_can_accept(session, driver, ride)

        ride.status = ACCEPTED
        ride.driver_id = driver_id
        ride.accepted_at = ride_rules.now()
        if not ride_repository.update_if_status(session, ride, PENDING):
            # Another driver, a cancellation or the expiry got there first.
            raise Conflict(_why_not_offered(session, ride_id))
        logger.info("Ride accepted", extra={"context": {"rideId": ride.id, "driverId": driver_id}})
        return _present(session, ride, driver_id)


def release_ride(driver_id: int, ride_id: int) -> Ride:
    """The driver gives the ride up before it starts: it is offered again, the rider pays nothing more."""
    with database.session() as session:
        ride = _held_ride(session, ride_id, driver_id)
        if ride.status != ACCEPTED:
            raise Conflict(NOT_ACCEPTED)

        now = ride_rules.now()
        ride.status = PENDING
        ride.driver_id = None
        ride.accepted_at = None
        # Contract 6.8: 15 more minutes to find a driver, or until its time if later.
        ride.expires_at = max(now + ride_rules.DRIVER_SEARCH_DELAY, ride.scheduled_at or now)
        if not ride_repository.update_if_status(session, ride, ACCEPTED):
            raise Conflict(NOT_ACCEPTED)
        # Not stored (H11): a line in the logs only.
        logger.info("Ride released", extra={"context": {"rideId": ride.id, "driverId": driver_id}})
        return _present(session, ride, driver_id)


def start_ride(driver_id: int, ride_id: int) -> Ride:
    """The rider is on board. Starting again a started ride returns it."""
    with database.session() as session:
        ride = _held_ride(session, ride_id, driver_id)
        if ride.status == IN_PROGRESS:
            return _present(session, ride, driver_id)
        if ride.status != ACCEPTED:
            raise Conflict(NOT_ACCEPTED)
        now = ride_rules.now()
        if ride.scheduled_at is not None and ride.scheduled_at - now > ride_rules.START_WINDOW:
            raise Conflict(TOO_EARLY)

        ride.status = IN_PROGRESS
        ride.started_at = now
        if not ride_repository.update_if_status(session, ride, ACCEPTED):
            # Cancelled by the rider at the same moment.
            raise Conflict(NOT_ACCEPTED)
        logger.info("Ride started", extra={"context": {"rideId": ride.id}})
        return _present(session, ride, driver_id)


def complete_ride(driver_id: int, ride_id: int) -> Ride:
    """Arrived. Completing again a completed ride returns it."""
    with database.session() as session:
        ride = _held_ride(session, ride_id, driver_id)
        if ride.status == COMPLETED:
            return _present(session, ride, driver_id)
        if ride.status != IN_PROGRESS:
            raise Conflict(NOT_IN_PROGRESS)

        ride.status = COMPLETED
        ride.completed_at = ride_rules.now()
        if not ride_repository.update_if_status(session, ride, IN_PROGRESS):
            raise Conflict(NOT_IN_PROGRESS)
        logger.info("Ride completed", extra={"context": {"rideId": ride.id}})
        return _present(session, ride, driver_id)


# --- Helpers -----------------------------------------------------------------

def _online_driver(session: Session, driver_id: int) -> User:
    driver = user_repository.find_by_id(session, driver_id)
    if not driver.is_available:
        raise Conflict(OFFLINE)
    return driver


def _accessible(driver: User) -> bool:
    return driver.vehicle is not None and driver.vehicle.is_accessible


def _recent_position(driver: User) -> Location | None:
    location = driver.location
    if location is None or ride_rules.now() - location.at > ride_rules.LOCATION_MAX_AGE:
        return None
    return location


def _distance(position: Location, ride: Ride) -> float:
    return straight_distance_km(position.lat, position.lng, ride.pickup.lat, ride.pickup.lng)


def _find(session: Session, ride_id: int) -> Ride:
    ride = ride_repository.find_by_id(session, ride_id)
    if ride is None:
        raise NotFound(RIDE_NOT_FOUND)
    return ride


def _held_ride(session: Session, ride_id: int, driver_id: int) -> Ride:
    """A ride the driver holds. 404 if it was never theirs; 409 once they gave it up."""
    ride = _find(session, ride_id)
    if ride.driver_id != driver_id:
        if ride.status == PENDING:
            raise Conflict(NOT_YOUR_RIDE)
        raise NotFound(RIDE_NOT_FOUND)
    return ride


def _check_can_accept(session: Session, driver: User, ride: Ride) -> None:
    if ride.status != PENDING:
        raise Conflict(_why_not_offered(session, ride.id))
    now = ride_rules.now()
    if ride.expires_at <= now:
        raise Conflict(NO_LONGER_OFFERED)
    if ride.needs_accessible_vehicle and not _accessible(driver):
        raise Conflict(NEEDS_ACCESSIBLE_VEHICLE)
    held = ride_repository.find_driver_rides(session, driver.id, ride_rules.HELD_STATUSES)
    held_times = [ride_rules.ride_time(other.scheduled_at, now) for other in held]
    if ride_rules.too_close(ride_rules.ride_time(ride.scheduled_at, now), held_times):
        raise Conflict(TIMETABLE_CLASH)


def _why_not_offered(session: Session, ride_id: int) -> str:
    ride = ride_repository.find_by_id(session, ride_id)
    if ride.status in ride_rules.HELD_STATUSES or ride.status == COMPLETED:
        return ALREADY_TAKEN
    return NO_LONGER_OFFERED


def _present(session: Session, ride: Ride, driver_id: int) -> Ride:
    return present(session, [ride], user_id=driver_id, role=DRIVER)[0]
