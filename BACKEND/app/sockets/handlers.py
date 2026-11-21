"""
Events received on the real-time channel (contract, part 5).

Like a controller, a handler holds no business rule: it checks who is
calling, then asks a service. A page subscribes to what it shows:

- ride:follow {rideId}   the page of a ride (its rider, its driver, the staff);
- offers:follow          the driver's list of rides to take.

Every subscription answers { accepted: true | false }. Refused, the page keeps
working with its "Actualiser" button.
"""

import logging

from flask import request
from flask_socketio import join_room, leave_room
from pydantic import ValidationError

from ..dtos.realtime_dto import FollowRideInput, SubscriptionAck
from ..extensions import socketio
from ..services import ride_service
from ..services.account_rules import DRIVER
from ..utils import access
from ..utils.access import SessionAccount, SocketCaller
from .broadcast import DRIVERS_ROOM, ride_room

logger = logging.getLogger(__name__)

# Who opened each connection, by Socket.IO id. In memory, like the other state
# of a single API process (ADR 007); emptied at the disconnection.
_callers: dict[str, SocketCaller] = {}

SUBSCRIBED = SubscriptionAck(accepted=True).to_json()
NOT_SUBSCRIBED = SubscriptionAck(accepted=False).to_json()


@socketio.on("connect")
def on_connect(_auth=None) -> bool:
    """Only a logged-in person may open the channel: False refuses the connection."""
    caller = access.socket_caller()
    if caller is None:
        return False
    _callers[request.sid] = caller
    logger.info("Real-time client connected", extra={"context": {"userId": caller.user_id}})
    return True


@socketio.on("disconnect")
def on_disconnect(*_) -> None:
    # Socket.IO takes the connection out of its rooms by itself.
    _callers.pop(request.sid, None)


@socketio.on("ride:follow")
def on_follow_ride(message: object) -> dict:
    ride_id = _ride_id(message)
    account = _current_account()
    if ride_id is None or account is None:
        return NOT_SUBSCRIBED
    allowed = ride_service.may_follow(user_id=account.id, role=account.role, ride_id=ride_id)
    if not allowed:
        # As GET /rides/{id} answers 404: the caller does not learn whether the ride exists.
        logger.info("Ride follow refused", extra={"context": {"userId": account.id, "rideId": ride_id}})
        return NOT_SUBSCRIBED
    join_room(ride_room(ride_id))
    return SUBSCRIBED


@socketio.on("ride:unfollow")
def on_unfollow_ride(message: object) -> dict:
    ride_id = _ride_id(message)
    if ride_id is None:
        return NOT_SUBSCRIBED
    leave_room(ride_room(ride_id))
    return SUBSCRIBED


@socketio.on("offers:follow")
def on_follow_offers(*_) -> dict:
    """The list of rides to take. The signal says nothing of a ride: the list
    read again afterwards applies the rules of the offers (online, distance, vehicle)."""
    account = _current_account()
    if account is None or account.role != DRIVER:
        return NOT_SUBSCRIBED
    join_room(DRIVERS_ROOM)
    return SUBSCRIBED


@socketio.on("offers:unfollow")
def on_unfollow_offers(*_) -> dict:
    leave_room(DRIVERS_ROOM)
    return SUBSCRIBED


def _current_account() -> SessionAccount | None:
    """The account of this connection, read again now: None once suspended or logged out elsewhere."""
    caller = _callers.get(request.sid)
    if caller is None:
        return None
    return access.socket_account(caller)


def _ride_id(message: object) -> int | None:
    try:
        follow = FollowRideInput.model_validate(message)
    except ValidationError:
        return None
    return follow.ride_id
