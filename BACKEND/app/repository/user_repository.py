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
from dataclasses import dataclass, field
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
    # partner
    partner_id: int | None = None
    id: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class DuplicateValue(Exception):
    """Phone or e-mail already used: what a unique constraint raises in a real database."""


_lock = threading.Lock()
_users: dict[int, User] = {}
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


def _check_unique(user: User) -> None:
    for other in _users.values():
        if other.id == user.id:
            continue
        if other.phone == user.phone or (user.email is not None and other.email == user.email):
            raise DuplicateValue


# --- Development accounts ----------------------------------------------------
# Fictitious people only (GDPR). Listed in the README, part "Comptes de test".
DEV_PASSWORD = "Trajet-2026!"
DEV_ACTIVATION_CODE = "12345678"
_DEV_ACTIVATION_CODE_VALIDITY = timedelta(days=365)

# Hashing is slow on purpose: done once, not at every reset of the tests.
_DEV_PASSWORD_HASH = hash_secret(DEV_PASSWORD)
_DEV_ACTIVATION_CODE_HASH = hash_secret(DEV_ACTIVATION_CODE)


def _dev_accounts() -> list[User]:
    def account(role: str, first_name: str, number: str, **profile) -> User:
        return User(
            role=role,
            status=profile.pop("status", "active"),
            first_name=first_name,
            last_name="Démo",
            phone=f"+59469400000{number}",
            password_hash=profile.pop("password_hash", _DEV_PASSWORD_HASH),
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
            activation_code_hash=_DEV_ACTIVATION_CODE_HASH,
            activation_code_expires_at=datetime.now(timezone.utc) + _DEV_ACTIVATION_CODE_VALIDITY,
        ),
        account("rider", "Hugo", "8", status="suspended"),
    ]


def reset() -> None:
    """Back to the development accounts only. Called at startup and by the tests."""
    global _next_id
    with _lock:
        _users.clear()
        _next_id = 1
    for user in _dev_accounts():
        insert_user(None, user)  # type: ignore[arg-type]


reset()
