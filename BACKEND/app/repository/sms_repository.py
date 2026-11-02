"""
SMS to the users, through an SMS gateway (UC62).

SIMULATED in the MVP: one log line per SMS, never sent. The line carries the
kind of message and the account, never the phone number nor the text (GDPR).
The only place that will talk to the real gateway: switching to it only
changes this file.

Which messages exactly is still to settle with the client (contract,
question 4).
"""

import logging

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# No driver took the ride in time: it is cancelled and refunded.
RIDE_EXPIRED_NO_DRIVER = "ride_expired_no_driver"


def send(_session: Session, *, user_id: int, kind: str, ride_id: int | None = None) -> None:
    logger.info("SMS simulated", extra={"context": {"kind": kind, "userId": user_id, "rideId": ride_id}})
