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
# Registration (audit F4): the code that proves the phone, or, when the number
# already has an account, a message saying so instead of a code.
REGISTRATION_CODE = "registration_code"
ALREADY_REGISTERED = "already_registered"
# An administrator issued a new activation code for an account that already
# has a password (audit F19): its holder is warned.
NEW_ACTIVATION_CODE = "new_activation_code"
# A rider was suspended: their rides not taken yet are cancelled and refunded.
SUSPENDED_RIDES_CANCELLED = "suspended_rides_cancelled"


def send(_session: Session, *, user_id: int, kind: str, ride_id: int | None = None) -> None:
    logger.info("SMS simulated", extra={"context": {"kind": kind, "userId": user_id, "rideId": ride_id}})


def send_to_number(_session: Session, *, phone: str, kind: str, code: str | None = None) -> None:
    """To a number without an account yet (registration). `code`: the code to send in it.

    Neither the number nor the code reaches the logs (the code would open the
    account): the real gateway will receive them, the simulation drops them.
    """
    del phone, code
    logger.info("SMS simulated", extra={"context": {"kind": kind}})
