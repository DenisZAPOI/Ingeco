"""
Real-time channel (Flask-SocketIO): ride tracking, driver position, new ride
offers.

Like a controller, a handler holds no business rule: it calls a service, which
decides. Services emit events through broadcast.py, AFTER their transaction is
committed: an event emitted then cancelled by a rollback would announce a state
that never existed.

Handled for now: connection and disconnection, so the front-end can check the
channel works.
"""

import logging

from flask import request
from flask_socketio import emit

from ..extensions import socketio

logger = logging.getLogger(__name__)


@socketio.on("connect")
def on_connect():
    logger.info("Real-time client connected", extra={"context": {"socketId": request.sid}})
    emit("welcome", {"message": "Real-time channel ready"})


@socketio.on("disconnect")
def on_disconnect(*_):
    logger.info("Real-time client disconnected", extra={"context": {"socketId": request.sid}})
