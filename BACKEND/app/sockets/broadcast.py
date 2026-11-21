"""
Emission of real-time events (contract, part 5).

The events are signals, not data: `ride:updated` gives the ride's id and new
status, `offers:changed` nothing at all. The page that receives one reads the
ride again over HTTP (GET /rides/{id}, GET /drivers/me/ride-offers), so what
each person may see stays decided by the services in one place (present()):
the rider and the driver never see the same fields.

Services call ride_changed() inside their transaction: the emission waits
for the commit (database.after_commit), and never happens after a rollback.
"""

from sqlalchemy.orm import Session

from ..extensions import socketio
from ..repository.ride_repository import Ride
from ..services.ride_rules import PENDING
from ..utils import database

RIDE_UPDATED = "ride:updated"
OFFERS_CHANGED = "offers:changed"
# The drivers looking at the list of rides to take (offers:follow).
DRIVERS_ROOM = "drivers"


def ride_room(ride_id: int) -> str:
    """The people following one ride: its rider, its driver, the staff (ride:follow)."""
    return f"ride:{ride_id}"


def ride_changed(session: Session, ride: Ride, previous_status: str | None) -> None:
    """Tells, once the transaction is committed, that `ride` went from `previous_status` to its status.

    `previous_status` is None for a ride just booked. Only the id and status
    of `ride` are read, now: the event tells the state this transaction wrote.
    """
    ride_id = ride.id
    status = ride.status
    # A ride that enters or leaves the waiting list changes the drivers' offers.
    offers_changed = PENDING in (previous_status, status)

    def emit() -> None:
        socketio.emit(RIDE_UPDATED, {"rideId": ride_id, "status": status}, to=ride_room(ride_id))
        if offers_changed:
            socketio.emit(OFFERS_CHANGED, to=DRIVERS_ROOM)

    database.after_commit(session, emit)
