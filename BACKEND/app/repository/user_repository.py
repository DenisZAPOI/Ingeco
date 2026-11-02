"""
User accounts.

FAKE DATA until the DB team delivers the schema: accounts live in memory and
are reset at every restart. The function signatures are those the real
repository will keep (the session comes first, unused for now): when the
schema arrives, only the bodies of these functions change.

Like a database, this store hands out COPIES: changing a returned object
changes nothing until update_user() is called.
"""

import copy
import threading
import unicodedata
from dataclasses import dataclass, field
from functools import cache
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..utils.passwords import hash_secret


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
    # partner
    partner_id: int | None = None
    # Changed by a new password or a suspension: the sessions opened with an
    # older version end (column to add, see README part 5).
    session_version: int = 0
    id: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class Position:
    """Where a page of accounts stopped: the next page starts after this account."""

    created_at: datetime
    user_id: int


class DuplicateValue(Exception):
    """Phone, e-mail or plate already used: what a unique constraint raises in a real database."""


_lock = threading.Lock()
_users: dict[int, User] = {}
# Apart from the accounts, like the BLOB column read only by the photo route:
# a list of accounts never carries the images.
_photos: dict[int, bytes] = {}
_next_id = 1


def find_by_id(_session: Session, user_id: int) -> User | None:
    with _lock:
        user = _users.get(user_id)
        return copy.deepcopy(user) if user else None


def find_by_phone(_session: Session, phone: str) -> User | None:
    with _lock:
        user = next((user for user in _users.values() if user.phone == phone), None)
        return copy.deepcopy(user) if user else None


def email_taken(_session: Session, email: str, except_user_id: int | None = None) -> bool:
    with _lock:
        return any(user.email == email and user.id != except_user_id for user in _users.values())


def plate_taken(_session: Session, plate: str, except_user_id: int | None = None) -> bool:
    with _lock:
        return any(
            user.vehicle is not None and user.vehicle.plate == plate and user.id != except_user_id
            for user in _users.values()
        )


def insert_user(_session: Session, user: User) -> User:
    """Stores a new account and returns it with its id."""
    global _next_id
    with _lock:
        _check_unique(user)
        stored = copy.deepcopy(user)
        stored.id = _next_id
        stored.created_at = datetime.now(timezone.utc)
        _users[stored.id] = stored
        _next_id += 1
        return copy.deepcopy(stored)


def update_user(_session: Session, user: User) -> None:
    with _lock:
        _check_unique(user)
        _users[user.id] = copy.deepcopy(user)


def set_availability(_session: Session, driver_id: int, available: bool) -> None:
    """Online or offline. Offline also erases the last position (GDPR, H6)."""
    with _lock:
        driver = _users[driver_id]
        driver.is_available = available
        if not available:
            driver.location = None


def set_location(_session: Session, driver_id: int, location: Location) -> bool:
    """Keeps the last position of an online driver. False if they are offline.

    The most frequent write of the API: one row, one UPDATE, no read before
    (`UPDATE chauffeur … WHERE id_utilisateur = :id AND est_disponible`).
    """
    with _lock:
        driver = _users[driver_id]
        if not driver.is_available:
            return False
        driver.location = copy.deepcopy(location)
        return True


def find_page(
    _session: Session,
    *,
    name: str | None,
    phone_prefix: str | None,
    role: str | None,
    status: str | None,
    after: Position | None,
    limit: int,
) -> list[User]:
    """Accounts, the most recently created first, at most `limit`, starting after `after`.

    `name`: contained in the first name, the last name or both (ignoring case
    and accents, like the utf8mb4_unicode_ci collation). `phone_prefix`: the
    start of the stored number. Filters served by idx_utilisateur_role.
    """
    wanted = _fold(name) if name is not None else None
    with _lock:
        users = [
            user
            for user in _users.values()
            if (role is None or user.role == role)
            and (status is None or user.status == status)
            and (phone_prefix is None or user.phone.startswith(phone_prefix))
            and (wanted is None or wanted in _fold(f"{user.first_name} {user.last_name}"))
        ]
        users.sort(key=lambda user: (user.created_at, user.id), reverse=True)
        if after is not None:
            users = [user for user in users if (user.created_at, user.id) < (after.created_at, after.user_id)]
        return [copy.deepcopy(user) for user in users[:limit]]


def save_photo(_session: Session, driver_id: int, image: bytes, at: datetime) -> None:
    """Saves or replaces the photo of a driver, with its date (for the phones' cache)."""
    with _lock:
        _photos[driver_id] = image
        _users[driver_id].photo_updated_at = at


def find_photo(_session: Session, driver_id: int) -> bytes | None:
    with _lock:
        return _photos.get(driver_id)


def find_by_ids(_session: Session, user_ids: set[int]) -> dict[int, User]:
    with _lock:
        return {user_id: copy.deepcopy(_users[user_id]) for user_id in user_ids if user_id in _users}


def _check_unique(user: User) -> None:
    for other in _users.values():
        if other.id == user.id:
            continue
        if other.phone == user.phone or (user.email is not None and other.email == user.email):
            raise DuplicateValue
        if user.vehicle is not None and other.vehicle is not None and other.vehicle.plate == user.vehicle.plate:
            raise DuplicateValue


def _fold(text: str) -> str:
    """'Chloé' → 'chloe': what an accent- and case-insensitive collation compares."""
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(character for character in decomposed if not unicodedata.combining(character))


# --- Development accounts ----------------------------------------------------
# Fictitious people only (GDPR). Listed in the README, part "Comptes de test".
# Their password is public: loaded only with LOAD_DEMO_DATA=true (see main.py),
# never in a hosted environment.
DEV_PASSWORD = "Trajet-2026!"
DEV_ACTIVATION_CODE = "12345678"
_DEV_ACTIVATION_CODE_VALIDITY = timedelta(days=365)


@cache
def _dev_hashes() -> tuple[str, str]:
    """Hashing is slow on purpose: done once, and only if the demo is loaded."""
    return hash_secret(DEV_PASSWORD), hash_secret(DEV_ACTIVATION_CODE)


def _dev_accounts() -> list[User]:
    password_hash, activation_code_hash = _dev_hashes()

    def account(role: str, first_name: str, number: str, **profile) -> User:
        return User(
            role=role,
            status=profile.pop("status", "active"),
            first_name=first_name,
            last_name="Démo",
            phone=f"+59469400000{number}",
            password_hash=profile.pop("password_hash", password_hash),
            **profile,
        )

    return [
        account("rider", "Alice", "1"),
        account("rider", "Bruno", "2", is_priority=True, needs_accessible_vehicle=True),
        account(
            "driver", "Chloé", "3",
            vehicle=Vehicle(plate="AA-001-AA", model="Véhicule fictif", seats=4, is_accessible=True),
        ),
        account("partner", "David", "4", partner_id=1),
        account("operator", "Emma", "5"),
        account("admin", "Farid", "6"),
        # Created by the call centre: no password yet, activates with the code.
        account(
            "rider", "Gaëlle", "7",
            password_hash=None,
            activation_code_hash=activation_code_hash,
            activation_code_expires_at=datetime.now(timezone.utc) + _DEV_ACTIVATION_CODE_VALIDITY,
        ),
        account("rider", "Hugo", "8", status="suspended"),
    ]


def reset(*, demo_accounts: bool = False) -> None:
    """Empties the store, then adds the development accounts if asked.

    Called at startup with LOAD_DEMO_DATA, and by the tests. The store starts
    empty: without the flag, no account with a public password exists.
    """
    global _next_id
    with _lock:
        _users.clear()
        _photos.clear()
        _next_id = 1
    if demo_accounts:
        for user in _dev_accounts():
            insert_user(None, user)  # type: ignore[arg-type]
