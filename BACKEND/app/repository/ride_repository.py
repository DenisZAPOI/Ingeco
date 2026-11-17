"""
Rides (table `course` of the DB team), their ratings (table `evaluation`) and
their log (table `etape_course`, migration 023).

The rides of the demonstration come from sql/demo-data.sql; the API creates
none itself. Like any repository, this one hands out plain objects: changing
a returned Ride changes nothing until a write function is called.

The values of the ENUM columns are in French in the rows ('en_attente',
'emploi', 'paye'…) and in English in the API ('pending', 'employment',
'paid'…): the translation is done here, and only here.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timezone, tzinfo
from decimal import Decimal

from sqlalchemy import Select, false, func, or_, select, tuple_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import RatingRow, RideRow, RideStepRow

_STATUS_TO_ROW = {
    "awaiting_payment": "attente_paiement",
    "pending": "en_attente",
    "accepted": "acceptee",
    "in_progress": "en_cours",
    "completed": "terminee",
    "cancelled": "annulee",
    "expired": "expiree",
}
_PAYMENT_TO_ROW = {"not_required": "non_requis", "pending": "en_attente", "paid": "paye", "refunded": "rembourse"}
_PURPOSE_TO_ROW = {
    "employment": "emploi",
    "training": "formation",
    "health": "sante",
    "administrative": "demarche_administrative",
    "other": "autre",
}
_CHANNEL_TO_ROW = {"app": "application", "phone": "telephone"}
# Kinds of step of the log (ENUM etape_course.type).
_STEP_TO_ROW = {
    "created": "creee",
    "paid": "payee",
    "payment_failed": "paiement_echoue",
    "accepted": "acceptee",
    "released": "desistement",
    "driver_arrived": "chauffeur_arrive",
    "started": "demarree",
    "completed": "terminee",
    "cancelled": "annulee",
    "expired": "expiree",
    "no_show": "passager_absent",
    "refunded": "remboursee",
    "incident": "incident",
}


def _reverse(mapping: dict[str, str]) -> dict[str, str]:
    return {row: value for value, row in mapping.items()}


_STATUS_FROM_ROW = _reverse(_STATUS_TO_ROW)
_PAYMENT_FROM_ROW = _reverse(_PAYMENT_TO_ROW)
_PURPOSE_FROM_ROW = _reverse(_PURPOSE_TO_ROW)
_CHANNEL_FROM_ROW = _reverse(_CHANNEL_TO_ROW)
_STEP_FROM_ROW = _reverse(_STEP_TO_ROW)


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
class Step:
    """One line of the log of a ride: what happened, when, and who did it
    (None: the application itself, as for an expiry)."""

    kind: str
    at: datetime
    author_id: int | None
    comment: str | None = None


@dataclass(frozen=True)
class LoggedStep:
    """A line of the log as it is read back, with its ride."""

    ride_id: int
    kind: str
    at: datetime
    author_id: int | None
    comment: str | None


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
    """client_request_id already used: the unique key of `course` refused it."""


class AlreadyRated(Exception):
    """The ride already has a rating: the primary key of `evaluation` refused it."""


def find_by_id(session: Session, ride_id: int) -> Ride | None:
    found = session.execute(_with_rating().where(RideRow.id == ride_id)).first()
    return _to_ride(*found) if found else None


def find_by_client_request_id(session: Session, client_request_id: str) -> Ride | None:
    found = session.execute(_with_rating().where(RideRow.client_request_id == client_request_id)).first()
    return _to_ride(*found) if found else None


def find_upcoming(
    session: Session, *, rider_id: int | None, driver_id: int | None, statuses: tuple[str, ...]
) -> list[Ride]:
    """Rides of a rider (or of a driver) in one of `statuses`, the soonest first.

    The soonest: by scheduled time, or by booking time for an immediate ride.
    """
    query = (
        _with_rating()
        .where(_belongs(rider_id, driver_id), _in_statuses(statuses))
        .order_by(func.coalesce(RideRow.scheduled_at, RideRow.created_at), RideRow.id)
    )
    return [_to_ride(*found) for found in session.execute(query)]


def find_pending(session: Session, *, scheduled: bool, accessible_vehicle: bool) -> list[Ride]:
    """Rides waiting for a driver: immediate ones, or scheduled ones by date.

    A driver without an accessible vehicle never sees a ride that needs one.
    Served by the index idx_course_statut_prevue (statut, prevue_le).
    """
    query = _with_rating().where(
        RideRow.status == _STATUS_TO_ROW["pending"],
        RideRow.scheduled_at.is_not(None) if scheduled else RideRow.scheduled_at.is_(None),
    )
    if not accessible_vehicle:
        query = query.where(RideRow.needs_accessible_vehicle.is_(False))
    query = query.order_by(func.coalesce(RideRow.scheduled_at, RideRow.created_at), RideRow.id)
    return [_to_ride(*found) for found in session.execute(query)]


def find_driver_rides(session: Session, driver_id: int, statuses: tuple[str, ...]) -> list[Ride]:
    """The rides a driver holds in one of `statuses` (to check their timetable)."""
    query = _with_rating().where(RideRow.driver_id == driver_id, _in_statuses(statuses))
    return [_to_ride(*found) for found in session.execute(query)]


def average_scores(session: Session, driver_ids: set[int]) -> dict[int, float]:
    """Average rating of each driver, over their rated rides. A driver never rated is absent."""
    if not driver_ids:
        return {}
    query = (
        select(RideRow.driver_id, func.avg(RatingRow.score))
        .join(RatingRow, RatingRow.ride_id == RideRow.id)
        .where(RideRow.driver_id.in_(driver_ids))
        .group_by(RideRow.driver_id)
    )
    return {driver_id: float(average) for driver_id, average in session.execute(query)}


def find_page(
    session: Session,
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
    query = _with_rating().where(_belongs(rider_id, driver_id), _in_statuses(statuses))
    if after is not None:
        query = query.where(tuple_(RideRow.created_at, RideRow.id) < tuple_(after.created_at, after.ride_id))
    query = query.order_by(RideRow.created_at.desc(), RideRow.id.desc()).limit(limit)
    return [_to_ride(*found) for found in session.execute(query)]


def find_due(session: Session, statuses: tuple[str, ...], now: datetime) -> list[Ride]:
    """Rides still in one of `statuses` whose deadline (expires_at) is past.

    Served by idx_course_expiration (statut, expire_le). Run every minute.
    """
    query = _with_rating().where(_in_statuses(statuses), RideRow.expires_at < now).order_by(RideRow.id)
    return [_to_ride(*found) for found in session.execute(query)]


def earnings_by_day(
    session: Session, driver_id: int, start: datetime, end: datetime, local_time: tzinfo
) -> list[DayEarnings]:
    """The driver's completed rides from `start` (included) to `end` (excluded),
    counted and summed per day of completion in `local_time`, the most recent day first.

    The rows are grouped here rather than in SQL: the local day depends on
    the time zone of the API (ride_rules.GUYANA_TIME), and a month holds a few
    dozen rides at most. Served by idx_course_chauffeur.
    """
    query = select(RideRow.completed_at, RideRow.price_cents).where(
        RideRow.driver_id == driver_id,
        RideRow.status == _STATUS_TO_ROW["completed"],
        RideRow.completed_at >= start,
        RideRow.completed_at < end,
    )
    days: dict[date, list[int]] = {}
    for completed_at, price_cents in session.execute(query):
        totals = days.setdefault(completed_at.astimezone(local_time).date(), [0, 0])
        totals[0] += 1
        totals[1] += price_cents
    return [
        DayEarnings(day=day, ride_count=count, total_cents=total)
        for day, (count, total) in sorted(days.items(), reverse=True)
    ]


def insert_ride(session: Session, ride: Ride, step: Step) -> Ride:
    """Stores a new ride and the first line of its log; returns the ride with its id.

    DuplicateRequest if its client_request_id is already used (a booking sent
    twice on a slow network): a savepoint keeps the session usable.
    """
    row = RideRow()
    _copy_to_row(ride, row)
    try:
        with session.begin_nested():
            session.add(row)
            session.flush()
    except IntegrityError as error:
        if session.scalar(select(RideRow.id).where(RideRow.client_request_id == ride.client_request_id)):
            raise DuplicateRequest from error
        raise
    _log(session, row.id, step)
    stored = find_by_id(session, row.id)
    assert stored is not None
    return stored


def update_if_status(session: Session, ride: Ride, expected_status: str, steps: list[Step]) -> bool:
    """Writes the ride and its new log lines, only if its stored status is still `expected_status`.

    `UPDATE course … WHERE id_course = :id AND statut = :expected`: of two
    changes arriving at the same moment (two payments, two drivers accepting),
    only one succeeds. False for the other one, and nothing is logged.
    """
    values = _row_values(ride)
    result = session.execute(
        update(RideRow)
        .where(RideRow.id == ride.id, RideRow.status == _STATUS_TO_ROW[expected_status])
        .values(**values)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount != 1:
        return False
    for step in steps:
        _log(session, ride.id, step)
    return True


def insert_rating(session: Session, ride_id: int, rating: Rating) -> None:
    try:
        with session.begin_nested():
            session.add(
                RatingRow(ride_id=ride_id, score=rating.score, comment=rating.comment, created_at=rating.created_at)
            )
            session.flush()
    except IntegrityError as error:
        raise AlreadyRated from error


def find_steps(session: Session, ride_id: int) -> list[LoggedStep]:
    """The log of a ride, in order. Served by idx_etape_course_course."""
    query = (
        select(RideStepRow)
        .where(RideStepRow.ride_id == ride_id)
        .order_by(RideStepRow.happened_at, RideStepRow.id)
    )
    return [
        LoggedStep(
            ride_id=row.ride_id,
            kind=_STEP_FROM_ROW[row.kind],
            at=row.happened_at,
            author_id=row.author_id,
            comment=row.comment,
        )
        for row in session.scalars(query)
    ]


def _log(session: Session, ride_id: int, step: Step) -> None:
    """Never updated nor deleted afterwards (migration 023)."""
    session.add(
        RideStepRow(
            ride_id=ride_id,
            author_id=step.author_id,
            kind=_STEP_TO_ROW[step.kind],
            happened_at=step.at,
            comment=step.comment,
        )
    )
    session.flush()


def _with_rating() -> Select:
    """Each ride with its rating, or None (LEFT JOIN evaluation)."""
    return select(RideRow, RatingRow).outerjoin(RatingRow, RatingRow.ride_id == RideRow.id)


def _belongs(rider_id: int | None, driver_id: int | None):
    conditions = []
    if rider_id is not None:
        conditions.append(RideRow.rider_id == rider_id)
    if driver_id is not None:
        conditions.append(RideRow.driver_id == driver_id)
    # Neither: no ride belongs to nobody.
    return or_(*conditions) if conditions else false()


def _in_statuses(statuses: tuple[str, ...]):
    return RideRow.status.in_([_STATUS_TO_ROW[status] for status in statuses])


def _to_ride(row: RideRow, rating: RatingRow | None) -> Ride:
    return Ride(
        id=row.id,
        client_request_id=row.client_request_id,
        rider_id=row.rider_id,
        booked_by_id=row.booked_by_id,
        channel=_CHANNEL_FROM_ROW[row.channel],
        status=_STATUS_FROM_ROW[row.status],
        purpose=_PURPOSE_FROM_ROW[row.purpose],
        pickup=Stop(
            address=row.pickup_address,
            lat=float(row.pickup_lat),
            lng=float(row.pickup_lng),
            commune_id=row.pickup_commune_id,
        ),
        dropoff=Stop(
            address=row.dropoff_address,
            lat=float(row.dropoff_lat),
            lng=float(row.dropoff_lng),
            commune_id=row.dropoff_commune_id,
        ),
        scheduled_at=row.scheduled_at,
        needs_accessible_vehicle=row.needs_accessible_vehicle,
        distance_km=row.distance_km,
        tariff_id=row.tariff_id,
        price_cents=row.price_cents,
        payment_status=_PAYMENT_FROM_ROW[row.payment_status],
        expires_at=row.expires_at,
        driver_id=row.driver_id,
        paid_at=row.paid_at,
        accepted_at=row.accepted_at,
        started_at=row.started_at,
        completed_at=row.completed_at,
        cancelled_at=row.cancelled_at,
        expired_at=row.expired_at,
        cancelled_by_id=row.cancelled_by_id,
        created_at=row.created_at,
        rating=Rating(score=rating.score, comment=rating.comment, created_at=rating.created_at) if rating else None,
    )


def _row_values(ride: Ride) -> dict[str, object]:
    """The columns of `course` as written by an UPDATE (attribute names of RideRow)."""
    return {
        "client_request_id": ride.client_request_id,
        "rider_id": ride.rider_id,
        "driver_id": ride.driver_id,
        "booked_by_id": ride.booked_by_id,
        "channel": _CHANNEL_TO_ROW[ride.channel],
        "status": _STATUS_TO_ROW[ride.status],
        "purpose": _PURPOSE_TO_ROW[ride.purpose],
        "pickup_address": ride.pickup.address,
        "pickup_lat": _coordinate(ride.pickup.lat),
        "pickup_lng": _coordinate(ride.pickup.lng),
        "pickup_commune_id": ride.pickup.commune_id,
        "dropoff_address": ride.dropoff.address,
        "dropoff_lat": _coordinate(ride.dropoff.lat),
        "dropoff_lng": _coordinate(ride.dropoff.lng),
        "dropoff_commune_id": ride.dropoff.commune_id,
        "scheduled_at": ride.scheduled_at,
        "needs_accessible_vehicle": ride.needs_accessible_vehicle,
        "distance_km": ride.distance_km,
        "tariff_id": ride.tariff_id,
        "price_cents": ride.price_cents,
        "payment_status": _PAYMENT_TO_ROW[ride.payment_status],
        "expires_at": ride.expires_at,
        "created_at": ride.created_at,
        "paid_at": ride.paid_at,
        "accepted_at": ride.accepted_at,
        "started_at": ride.started_at,
        "completed_at": ride.completed_at,
        "cancelled_at": ride.cancelled_at,
        "expired_at": ride.expired_at,
        "cancelled_by_id": ride.cancelled_by_id,
    }


def _copy_to_row(ride: Ride, row: RideRow) -> None:
    for name, value in _row_values(ride).items():
        setattr(row, name, value)


def _coordinate(value: float) -> Decimal:
    """DECIMAL(9,6) in the schema: six decimals, about 10 cm."""
    return Decimal(str(round(value, 6)))
