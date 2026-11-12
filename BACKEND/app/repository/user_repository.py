"""
User accounts: tables utilisateur, usager, chauffeur and vehicule.

The accounts of the demonstration come from sql/demo-data.sql (README, part
"Comptes de test"); the API creates none itself.

Like any repository, this one hands out plain objects: changing a returned
User changes nothing until update_user() is called.
"""

from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterator

from sqlalchemy import exists, func, select, tuple_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import DriverRow, RiderRow, UserRow, VehicleRow

# The values of utilisateur.statut, in French in the rows (models/__init__.py).
_STATUS_TO_ROW = {"active": "actif", "suspended": "suspendu"}
_STATUS_FROM_ROW = {row: status for status, row in _STATUS_TO_ROW.items()}

_RIDER = "rider"
_DRIVER = "driver"

# Characters with a meaning in LIKE: typed by an administrator, they are
# searched as themselves.
_LIKE_ESCAPE = "\\"


@dataclass
class Vehicle:
    plate: str
    model: str
    seats: int
    is_accessible: bool


@dataclass
class Location:
    lat: float
    lng: float
    at: datetime


@dataclass
class User:
    role: str
    status: str
    first_name: str
    last_name: str
    phone: str
    email: str | None = None
    password_hash: str | None = None
    activation_code_hash: str | None = None
    activation_code_expires_at: datetime | None = None
    # rider
    is_priority: bool = False
    needs_accessible_vehicle: bool = False
    # driver
    is_available: bool = False
    vehicle: Vehicle | None = None
    # Last known position only, no history (H6); None when offline.
    location: Location | None = None
    # When the photo was last saved (the photo itself: find_photo); None without one.
    photo_updated_at: datetime | None = None
    # partner: their structure comes with the vouchers (schema-hors-scope.sql),
    # not loaded yet, so always None for now.
    partner_id: int | None = None
    # Changed by a new password or a suspension: the sessions opened with an
    # older version end (migration 001).
    session_version: int = 0
    id: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class Position:
    """Where a page of accounts stopped: the next page starts after this account."""

    created_at: datetime
    user_id: int


class DuplicateValue(Exception):
    """Phone, e-mail or plate already used: a unique constraint of the tables refused it."""


def find_by_id(session: Session, user_id: int) -> User | None:
    row = session.get(UserRow, user_id)
    return _to_users(session, [row])[0] if row else None


def find_by_phone(session: Session, phone: str) -> User | None:
    row = session.scalars(select(UserRow).where(UserRow.phone == phone)).one_or_none()
    return _to_users(session, [row])[0] if row else None


def find_by_ids(session: Session, user_ids: set[int]) -> dict[int, User]:
    if not user_ids:
        return {}
    rows = session.scalars(select(UserRow).where(UserRow.id.in_(user_ids))).all()
    return {user.id: user for user in _to_users(session, rows)}


def email_taken(session: Session, email: str, except_user_id: int | None = None) -> bool:
    condition = UserRow.email == email
    if except_user_id is not None:
        condition &= UserRow.id != except_user_id
    return bool(session.scalar(select(exists().where(condition))))


def plate_taken(session: Session, plate: str, except_user_id: int | None = None) -> bool:
    condition = VehicleRow.plate == plate
    if except_user_id is not None:
        condition &= VehicleRow.driver_id != except_user_id
    return bool(session.scalar(select(exists().where(condition))))


def insert_user(session: Session, user: User) -> User:
    """Stores a new account (and its rider or driver part) and returns it with its id."""
    # DATETIME keeps whole seconds: the page positions compare what is stored.
    row = UserRow(created_at=datetime.now(timezone.utc).replace(microsecond=0))
    _copy_to_row(user, row)
    with _unique_values(session):
        session.add(row)
        session.flush()
        if user.role == _RIDER:
            session.add(RiderRow(user_id=row.id))
        elif user.role == _DRIVER:
            session.add(DriverRow(user_id=row.id))
        session.flush()
        _write_role_part(session, row.id, user)
    return _to_users(session, [row])[0]


def update_user(session: Session, user: User) -> None:
    row = session.get(UserRow, user.id)
    if row is None:
        raise LookupError(f"No account {user.id}.")
    _copy_to_row(user, row)
    with _unique_values(session):
        _write_role_part(session, user.id, user)


def set_availability(session: Session, driver_id: int, available: bool) -> None:
    """Online or offline. Offline also erases the last position (GDPR, H6)."""
    values: dict[str, object] = {"is_available": available}
    if not available:
        values |= {"last_lat": None, "last_lng": None, "last_location_at": None}
    session.execute(update(DriverRow).where(DriverRow.user_id == driver_id).values(**values))


def set_location(session: Session, driver_id: int, location: Location) -> bool:
    """Keeps the last position of an online driver. False if they are offline.

    The most frequent write of the API: one row, one UPDATE, no read before.
    """
    result = session.execute(
        update(DriverRow)
        .where(DriverRow.user_id == driver_id, DriverRow.is_available.is_(True))
        .values(last_lat=_coordinate(location.lat), last_lng=_coordinate(location.lng), last_location_at=location.at)
    )
    return result.rowcount == 1  # type: ignore[attr-defined]


def find_page(
    session: Session,
    *,
    name: str | None,
    phone_prefix: str | None,
    role: str | None,
    status: str | None,
    after: Position | None,
    limit: int,
) -> list[User]:
    """Accounts, the most recently created first, at most `limit`, starting after `after`.

    `name`: contained in the first name, the last name or both; the
    utf8mb4_unicode_ci collation ignores case and accents. `phone_prefix`:
    the start of the stored number. Filters served by idx_utilisateur_role.
    """
    query = select(UserRow)
    if role is not None:
        query = query.where(UserRow.role == role)
    if status is not None:
        query = query.where(UserRow.status == _STATUS_TO_ROW[status])
    if phone_prefix is not None:
        query = query.where(UserRow.phone.like(_escape_like(phone_prefix) + "%", escape=_LIKE_ESCAPE))
    if name is not None:
        full_name = func.concat(UserRow.first_name, " ", UserRow.last_name)
        query = query.where(full_name.like("%" + _escape_like(name) + "%", escape=_LIKE_ESCAPE))
    if after is not None:
        query = query.where(tuple_(UserRow.created_at, UserRow.id) < tuple_(after.created_at, after.user_id))
    query = query.order_by(UserRow.created_at.desc(), UserRow.id.desc()).limit(limit)
    return _to_users(session, session.scalars(query).all())


def save_photo(session: Session, driver_id: int, image: bytes, at: datetime) -> None:
    """Saves or replaces the photo of a driver, with its date (for the phones' cache)."""
    session.execute(
        update(DriverRow).where(DriverRow.user_id == driver_id).values(photo=image, photo_updated_at=at)
    )


def find_photo(session: Session, driver_id: int) -> bytes | None:
    return session.scalar(select(DriverRow.photo).where(DriverRow.user_id == driver_id))


# --- Rows ↔ User ------------------------------------------------------------

def _copy_to_row(user: User, row: UserRow) -> None:
    row.role = user.role
    row.status = _STATUS_TO_ROW[user.status]
    row.first_name = user.first_name
    row.last_name = user.last_name
    row.phone = user.phone
    row.email = user.email
    row.password_hash = user.password_hash
    row.activation_code_hash = user.activation_code_hash
    row.activation_code_expires_at = user.activation_code_expires_at
    row.session_version = user.session_version


def _write_role_part(session: Session, user_id: int, user: User) -> None:
    """The rider or driver row, and the driver's vehicle. The photo has its own function."""
    if user.role == _RIDER:
        rider = session.get(RiderRow, user_id)
        if rider is not None:
            rider.is_priority = user.is_priority
            rider.needs_accessible_vehicle = user.needs_accessible_vehicle
    elif user.role == _DRIVER:
        driver = session.get(DriverRow, user_id)
        if driver is not None:
            driver.is_available = user.is_available
            driver.last_lat = _coordinate(user.location.lat) if user.location else None
            driver.last_lng = _coordinate(user.location.lng) if user.location else None
            driver.last_location_at = user.location.at if user.location else None
        _write_vehicle(session, user_id, user.vehicle)
    session.flush()


def _write_vehicle(session: Session, driver_id: int, vehicle: Vehicle | None) -> None:
    if vehicle is None:
        return
    row = session.scalars(select(VehicleRow).where(VehicleRow.driver_id == driver_id)).one_or_none()
    if row is None:
        row = VehicleRow(driver_id=driver_id)
        session.add(row)
    row.plate = vehicle.plate
    row.model = vehicle.model
    row.seats = vehicle.seats
    row.is_accessible = vehicle.is_accessible


def _to_users(session: Session, rows) -> list[User]:
    """The accounts with their rider or driver part: three queries for a whole page, not three per account."""
    ids = [row.id for row in rows]
    riders = {
        rider.user_id: rider for rider in session.scalars(select(RiderRow).where(RiderRow.user_id.in_(ids)))
    } if ids else {}
    drivers = {
        driver.user_id: driver for driver in session.scalars(select(DriverRow).where(DriverRow.user_id.in_(ids)))
    } if ids else {}
    vehicles = {
        vehicle.driver_id: vehicle
        for vehicle in session.scalars(select(VehicleRow).where(VehicleRow.driver_id.in_(ids)))
    } if ids else {}
    return [_to_user(row, riders.get(row.id), drivers.get(row.id), vehicles.get(row.id)) for row in rows]


def _to_user(row: UserRow, rider: RiderRow | None, driver: DriverRow | None, vehicle: VehicleRow | None) -> User:
    user = User(
        id=row.id,
        role=row.role,
        status=_STATUS_FROM_ROW[row.status],
        first_name=row.first_name,
        last_name=row.last_name,
        phone=row.phone,
        email=row.email,
        password_hash=row.password_hash,
        activation_code_hash=row.activation_code_hash,
        activation_code_expires_at=row.activation_code_expires_at,
        session_version=row.session_version,
        created_at=row.created_at,
    )
    if rider is not None:
        user.is_priority = rider.is_priority
        user.needs_accessible_vehicle = rider.needs_accessible_vehicle
    if driver is not None:
        user.is_available = driver.is_available
        user.photo_updated_at = driver.photo_updated_at
        if driver.last_lat is not None and driver.last_lng is not None and driver.last_location_at is not None:
            user.location = Location(lat=float(driver.last_lat), lng=float(driver.last_lng), at=driver.last_location_at)
    if vehicle is not None:
        user.vehicle = Vehicle(
            plate=vehicle.plate, model=vehicle.model, seats=vehicle.seats, is_accessible=vehicle.is_accessible
        )
    return user


@contextmanager
def _unique_values(session: Session) -> Iterator[None]:
    """Turns a refused unique value (phone, e-mail, plate) into DuplicateValue.

    A savepoint: the session stays usable, and the service decides what to
    answer (a 409 that rolls the whole transaction back).
    """
    try:
        with session.begin_nested():
            yield
    except IntegrityError as error:
        raise DuplicateValue from error


def _coordinate(value: float) -> Decimal:
    """DECIMAL(9,6) in the schema: six decimals, about 10 cm."""
    return Decimal(str(round(value, 6)))


def _escape_like(text: str) -> str:
    return (
        text.replace(_LIKE_ESCAPE, _LIKE_ESCAPE * 2).replace("%", _LIKE_ESCAPE + "%").replace("_", _LIKE_ESCAPE + "_")
    )
