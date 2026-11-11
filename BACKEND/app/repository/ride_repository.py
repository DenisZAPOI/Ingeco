"""
Rides (table `course` of the DB team) and their ratings (table `evaluation`).

FAKE DATA until the repositories switch to the database: rides live in memory
and are lost at every restart. The signatures are those the real repository
will keep (the session comes first, unused for now).

Like a database, this store hands out COPIES: changing a returned object
changes nothing until a write function is called.
"""

import copy
import threading
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone, tzinfo
from decimal import Decimal

from sqlalchemy.orm import Session


@dataclass
class Stop:
    address: str
    lat: float
    lng: float
    commune_id: int
    # Signature sent by the phone with a stop it books (place_service): checked,
    # never stored.
    token: str | None = None


@dataclass
class Rating:
    """Table `evaluation`: one at most per ride, its key is the ride."""

    score: int
    comment: str | None
    created_at: datetime


@dataclass
class Contact:
    """Someone the other party of a ride may need to call."""

    first_name: str
    phone: str | None


@dataclass
class DriverInfo:
    """The driver as the rider sees them (joins chauffeur, vehicule, evaluation)."""

    id: int
    first_name: str
    phone: str | None
    vehicle_plate: str
    vehicle_model: str
    vehicle_is_accessible: bool
    average_score: float | None
    # Date of the face photo, None without one or when the caller may not see
    # it: the photo route uses it in its address, so a new photo is reloaded.
    photo_updated_at: datetime | None = None


@dataclass
class Ride:
    client_request_id: str
    rider_id: int
    booked_by_id: int
    channel: str
    status: str
    purpose: str
    pickup: Stop
    dropoff: Stop
    scheduled_at: datetime | None
    needs_accessible_vehicle: bool
    distance_km: Decimal
    tariff_id: int
    price_cents: int
    payment_status: str
    expires_at: datetime
    driver_id: int | None = None
    paid_at: datetime | None = None
    accepted_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    expired_at: datetime | None = None
    cancelled_by_id: int | None = None
    # Read with the ride (LEFT JOIN evaluation), written by insert_rating() only.
    rating: Rating | None = None
    # Added by the services for the caller (who may see whom): never stored.
    driver: DriverInfo | None = None
    rider: Contact | None = None
    id: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class Position:
    """Where a page of rides stopped: the next page starts after this ride."""

    created_at: datetime
    ride_id: int


@dataclass(frozen=True)
class DayEarnings:
    day: date
    ride_count: int
    total_cents: int


class DuplicateRequest(Exception):
    """client_request_id already used: what the unique constraint raises in a real database."""


class AlreadyRated(Exception):
    """The ride already has a rating: what the primary key of `evaluation` raises."""


_lock = threading.Lock()
_rides: dict[int, Ride] = {}
_ratings: dict[int, Rating] = {}
_next_id = 1


def find_by_id(_session: Session, ride_id: int) -> Ride | None:
    with _lock:
        ride = _rides.get(ride_id)
        return _read(ride) if ride else None


def find_by_client_request_id(_session: Session, client_request_id: str) -> Ride | None:
    with _lock:
        ride = next((ride for ride in _rides.values() if ride.client_request_id == client_request_id), None)
        return _read(ride) if ride else None


def find_upcoming(
    _session: Session, *, rider_id: int | None, driver_id: int | None, statuses: tuple[str, ...]
) -> list[Ride]:
    """Rides of a rider (or of a driver) in one of `statuses`, the soonest first.

    The soonest: by scheduled time, or by booking time for an immediate ride.
    """
    with _lock:
        rides = [ride for ride in _rides.values() if _belongs(ride, rider_id, driver_id) and ride.status in statuses]
        rides.sort(key=lambda ride: (ride.scheduled_at or ride.created_at, ride.id))
        return [_read(ride) for ride in rides]


def find_pending(_session: Session, *, scheduled: bool, accessible_vehicle: bool) -> list[Ride]:
    """Rides waiting for a driver: immediate ones, or scheduled ones by date.

    A driver without an accessible vehicle never sees a ride that needs one.
    Served by the index idx_course_statut_prevue (statut, prevue_le).
    """
    with _lock:
        rides = [
            ride
            for ride in _rides.values()
            if ride.status == "pending"
            and (ride.scheduled_at is not None) == scheduled
            and (accessible_vehicle or not ride.needs_accessible_vehicle)
        ]
        rides.sort(key=lambda ride: (ride.scheduled_at or ride.created_at, ride.id))
        return [_read(ride) for ride in rides]


def find_driver_rides(_session: Session, driver_id: int, statuses: tuple[str, ...]) -> list[Ride]:
    """The rides a driver holds in one of `statuses` (to check their timetable)."""
    with _lock:
        return [_read(ride) for ride in _rides.values() if ride.driver_id == driver_id and ride.status in statuses]


def average_scores(_session: Session, driver_ids: set[int]) -> dict[int, float]:
    """Average rating of each driver, over their rated rides. A driver never rated is absent."""
    with _lock:
        scores: dict[int, list[int]] = {}
        for ride_id, rating in _ratings.items():
            driver_id = _rides[ride_id].driver_id
            if driver_id in driver_ids:
                scores.setdefault(driver_id, []).append(rating.score)
        return {driver_id: sum(values) / len(values) for driver_id, values in scores.items()}


def find_page(
    _session: Session,
    *,
    rider_id: int | None,
    driver_id: int | None,
    statuses: tuple[str, ...],
    after: Position | None,
    limit: int,
) -> list[Ride]:
    """Rides of a rider (or of a driver) in one of `statuses`, the most recently booked first.

    At most `limit` rides, starting after `after`: keyset pagination, so a ride
    booked between two pages neither repeats nor hides another one. Served by
    the indexes idx_course_usager and idx_course_chauffeur (…, cree_le).
    """
    with _lock:
        rides = [ride for ride in _rides.values() if _belongs(ride, rider_id, driver_id) and ride.status in statuses]
        rides.sort(key=lambda ride: (ride.created_at, ride.id), reverse=True)
        if after is not None:
            rides = [ride for ride in rides if (ride.created_at, ride.id) < (after.created_at, after.ride_id)]
        return [_read(ride) for ride in rides[:limit]]


def find_due(_session: Session, statuses: tuple[str, ...], now: datetime) -> list[Ride]:
    """Rides still in one of `statuses` whose deadline (expires_at) is past.

    Served by idx_course_expiration (statut, expire_le). Run every minute.
    """
    with _lock:
        return [_read(ride) for ride in _rides.values() if ride.status in statuses and ride.expires_at < now]


def earnings_by_day(
    _session: Session, driver_id: int, start: datetime, end: datetime, local_time: tzinfo
) -> list[DayEarnings]:
    """The driver's completed rides from `start` (included) to `end` (excluded),
    counted and summed per day of completion in `local_time`, the most recent day first.

    Like `SELECT DATE(terminee_le - INTERVAL 3 HOUR), COUNT(*), SUM(prix_centimes) ...
    WHERE id_chauffeur = :id AND statut = 'terminee' AND terminee_le >= :start
    AND terminee_le < :end GROUP BY 1`, served by idx_course_chauffeur.
    """
    with _lock:
        days: dict[date, list[int]] = {}
        for ride in _rides.values():
            if ride.driver_id != driver_id or ride.status != "completed" or ride.completed_at is None:
                continue
            if not start <= ride.completed_at < end:
                continue
            totals = days.setdefault(ride.completed_at.astimezone(local_time).date(), [0, 0])
            totals[0] += 1
            totals[1] += ride.price_cents
        return [
            DayEarnings(day=day, ride_count=count, total_cents=total)
            for day, (count, total) in sorted(days.items(), reverse=True)
        ]


def insert_ride(_session: Session, ride: Ride) -> Ride:
    """Stores a new ride and returns it with its id."""
    global _next_id
    with _lock:
        if any(other.client_request_id == ride.client_request_id for other in _rides.values()):
            raise DuplicateRequest
        stored = _write(ride)
        stored.id = _next_id
        _rides[stored.id] = stored
        _next_id += 1
        return _read(stored)


def update_if_status(_session: Session, ride: Ride, expected_status: str) -> bool:
    """Writes the ride only if its stored status is still `expected_status`.

    Like `UPDATE course … WHERE id_course = :id AND statut = :expected`: of two
    changes arriving at the same moment (two payments, two drivers accepting),
    only one succeeds. False for the other one.
    """
    with _lock:
        stored = _rides.get(ride.id)
        if stored is None or stored.status != expected_status:
            return False
        _rides[ride.id] = _write(ride)
        return True


def insert_rating(_session: Session, ride_id: int, rating: Rating) -> None:
    with _lock:
        if ride_id in _ratings:
            raise AlreadyRated
        _ratings[ride_id] = copy.deepcopy(rating)


def _belongs(ride: Ride, rider_id: int | None, driver_id: int | None) -> bool:
    return (rider_id is not None and ride.rider_id == rider_id) or (
        driver_id is not None and ride.driver_id == driver_id
    )


def _read(ride: Ride) -> Ride:
    """A copy of the stored ride with its rating, as a join would return it."""
    read = copy.deepcopy(ride)
    read.rating = copy.deepcopy(_ratings.get(ride.id))
    return read


def _write(ride: Ride) -> Ride:
    """What is stored of a ride: its rating lives in its own table."""
    stored = copy.deepcopy(ride)
    stored.rating = None
    stored.driver = None
    stored.rider = None
    return stored


def reset(*, dev_rides: bool = False) -> None:
    """Empties the store, then adds the development rides if asked (LOAD_DEMO_DATA)."""
    global _next_id
    with _lock:
        _rides.clear()
        _ratings.clear()
        _next_id = 1
    if dev_rides:
        for ride, rating in _dev_rides():
            stored = insert_ride(None, ride)  # type: ignore[arg-type]
            if rating is not None:
                insert_rating(None, stored.id, rating)  # type: ignore[arg-type]


# --- Development rides -------------------------------------------------------
# Past rides of Alice (account 1), so that "Mes trajets" and the rating can be
# tried before the driver side exists. Fictitious places (GDPR).
_DEV_RIDER_ID = 1
_DEV_DRIVER_ID = 3
_DEV_TARIFF_ID = 1
_DEV_DISTANCE_KM = Decimal("13.1")
_DEV_PRICE_CENTS = 1848  # 800 + 80 × 13.1, provisional tariff
_DEV_PAYMENT_DELAY = timedelta(minutes=15)
_CAYENNE = Stop(address="Mairie de Cayenne", lat=4.9372, lng=-52.3260, commune_id=1)
_MATOURY = Stop(address="Mairie de Matoury", lat=4.8470, lng=-52.3310, commune_id=3)


def _dev_rides() -> list[tuple[Ride, Rating | None]]:
    now = datetime.now(timezone.utc)

    def past_ride(days_ago: int, purpose: str) -> Ride:
        booked_at = now - timedelta(days=days_ago)
        return Ride(
            client_request_id=f"00000000-0000-4000-8000-{days_ago:012d}",
            rider_id=_DEV_RIDER_ID,
            booked_by_id=_DEV_RIDER_ID,
            channel="app",
            status="completed",
            purpose=purpose,
            pickup=_CAYENNE,
            dropoff=_MATOURY,
            scheduled_at=None,
            needs_accessible_vehicle=False,
            distance_km=_DEV_DISTANCE_KM,
            tariff_id=_DEV_TARIFF_ID,
            price_cents=_DEV_PRICE_CENTS,
            payment_status="paid",
            expires_at=booked_at + _DEV_PAYMENT_DELAY,
            paid_at=booked_at,
            created_at=booked_at,
        )

    def completed(days_ago: int, purpose: str) -> Ride:
        ride = past_ride(days_ago, purpose)
        ride.driver_id = _DEV_DRIVER_ID
        ride.accepted_at = ride.created_at + timedelta(minutes=2)
        ride.started_at = ride.created_at + timedelta(minutes=10)
        ride.completed_at = ride.created_at + timedelta(minutes=35)
        return ride

    def cancelled(days_ago: int) -> Ride:
        ride = past_ride(days_ago, "administrative")
        ride.status = "cancelled"
        ride.payment_status = "refunded"
        ride.cancelled_at = ride.created_at + timedelta(minutes=5)
        ride.cancelled_by_id = _DEV_RIDER_ID
        return ride

    first = completed(10, "employment")
    return [
        (first, Rating(score=5, comment=None, created_at=first.completed_at)),
        (cancelled(6), None),
        (completed(2, "health"), None),
        (completed(1, "training"), None),
    ]

