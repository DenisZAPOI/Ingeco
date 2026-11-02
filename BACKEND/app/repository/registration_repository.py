"""
Registrations waiting for their SMS code (audit F4).

The account is only created once the code proves the phone belongs to the
person: until then, the registration lives here, 10 minutes at most.

IN MEMORY, and not a table, by choice: nothing reaches the database before
the phone is proven. Lost when the API restarts (the person asks for a new
code), and not shared between several API processes: to replace by a table
or a shared store if the API ever runs several processes.
"""

import copy
import threading
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session


@dataclass
class PendingRegistration:
    phone: str
    first_name: str
    last_name: str
    email: str | None
    needs_accessible_vehicle: bool
    password_hash: str
    code_hash: str
    expires_at: datetime
    failed_attempts: int = 0


_lock = threading.Lock()
_pending: dict[str, PendingRegistration] = {}


def save(_session: Session, registration: PendingRegistration, now: datetime) -> None:
    """Stores a registration, replacing the previous one of the same number."""
    with _lock:
        # Purged here: a registration never confirmed leaves no trace.
        for phone in [phone for phone, other in _pending.items() if other.expires_at <= now]:
            del _pending[phone]
        _pending[registration.phone] = copy.deepcopy(registration)


def find(_session: Session, phone: str) -> PendingRegistration | None:
    with _lock:
        registration = _pending.get(phone)
        return copy.deepcopy(registration) if registration else None


def record_failure(_session: Session, phone: str) -> int:
    """One more wrong code for this number. Returns the count, 0 without registration."""
    with _lock:
        registration = _pending.get(phone)
        if registration is None:
            return 0
        registration.failed_attempts += 1
        return registration.failed_attempts


def delete(_session: Session, phone: str) -> None:
    with _lock:
        _pending.pop(phone, None)


def reset() -> None:
    """Empties the store. Called by the tests."""
    with _lock:
        _pending.clear()
