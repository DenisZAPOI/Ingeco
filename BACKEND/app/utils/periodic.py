"""
Periodic tasks of the API (expiry of the rides, UC60).

A background task of the API process, started by create_app(): nothing to
install nor to schedule on the server. Several processes may each run it (the
development reloader, several workers later): the tasks must stay harmless
when run twice, which conditional writes guarantee.

Disabled in the tests (PERIODIC_TASKS_ENABLED=false): they call the task
themselves, after moving the clock.
"""

import logging
from collections.abc import Callable

from flask_socketio import SocketIO

logger = logging.getLogger(__name__)


def start(socketio: SocketIO, name: str, interval_seconds: int, task: Callable[[], object]) -> None:
    """Runs `task` every `interval_seconds`, for as long as the process lives."""

    def loop() -> None:
        while True:
            socketio.sleep(interval_seconds)
            try:
                task()
            except Exception:
                # One failed run (database unreachable…) must not stop the next ones.
                logger.exception("Periodic task failed", extra={"context": {"task": name}})

    socketio.start_background_task(loop)
    logger.info("Periodic task started", extra={"context": {"task": name, "everySeconds": interval_seconds}})
