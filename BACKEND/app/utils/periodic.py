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


def start(
    socketio: SocketIO,
    name: str,
    interval_seconds: int,
    task: Callable[[], object],
    first_delay_seconds: int | None = None,
) -> None:
    """Runs `task` every `interval_seconds`, for as long as the process lives.

    The first run waits `first_delay_seconds` (by default, the interval): a
    daily task must not wait a day after each restart of the API.
    """

    def loop() -> None:
        delay = interval_seconds if first_delay_seconds is None else first_delay_seconds
        while True:
            socketio.sleep(delay)
            delay = interval_seconds
            try:
                task()
            except Exception:
                # One failed run (database unreachable…) must not stop the next ones.
                logger.exception("Periodic task failed", extra={"context": {"task": name}})

    socketio.start_background_task(loop)
    logger.info("Periodic task started", extra={"context": {"task": name, "everySeconds": interval_seconds}})
