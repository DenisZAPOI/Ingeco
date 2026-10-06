"""
Emission of real-time events.

Services call these functions AFTER their transaction is committed.
One room per ride: only the rider, the driver and the operator follow it.
"""

from ..extensions import socketio


def ride_room(ride_id: int) -> str:
    return f"ride:{ride_id}"


def ride_updated(ride_id: int, ride: dict) -> None:
    socketio.emit("ride:updated", ride, to=ride_room(ride_id))
