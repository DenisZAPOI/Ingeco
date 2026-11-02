"""
Rides (table `course` of the DB team).

FAKE DATA until the repositories switch to the database: rides live in memory
and are lost at every restart. The signatures are those the real repository
will keep (the session comes first, unused for now).

Like a database, this store hands out COPIES: changing a returned object
changes nothing until a write function is called.
"""

import copy
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session


@dataclass
class Stop:
    address: str
    lat: float
    lng: float
    commune_id: int


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
    id: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class DuplicateRequest(Exception):
    """client_request_id already used: what the unique constraint raises in a real database."""


_lock = threading.Lock()
_rides: dict[int, Ride] = {}
_next_id = 1


def find_by_id(_session: Session, ride_id: int) -> Ride | None:
    with _lock:
        ride = _rides.get(ride_id)
        return copy.deepcopy(ride) if ride else None


def find_by_client_request_id(_session: Session, client_request_id: str) -> Ride | None:
    with _lock:
        ride = next((ride for ride in _rides.values() if ride.client_request_id == client_request_id), None)
        return copy.deepcopy(ride) if ride else None


def insert_ride(_session: Session, ride: Ride) -> Ride:
    """Stores a new ride and returns it with its id."""
    global _next_id
    with _lock:
        if any(other.client_request_id == ride.client_request_id for other in _rides.values()):
            raise DuplicateRequest
        stored = copy.deepcopy(ride)
        stored.id = _next_id
        _rides[stored.id] = stored
        _next_id += 1
        return copy.deepcopy(stored)


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
        _rides[ride.id] = copy.deepcopy(ride)
        return True


def reset() -> None:
    """No ride. Called by the tests."""
    global _next_id
    with _lock:
        _rides.clear()
        _next_id = 1
