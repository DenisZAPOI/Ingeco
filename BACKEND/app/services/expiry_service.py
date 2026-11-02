"""
Expiry of the rides left without a driver (UC60), run every minute.

A ride not paid in time (awaiting_payment), or that no driver took in time
(pending), expires at its deadline (contract 6.8): 15 minutes after the
booking or the payment for an immediate ride, its time for a scheduled one.
A paid share is refunded in full (H17); a rider who paid and waited is told
by SMS (simulated, UC62). One who did not pay gave up by themselves: no SMS.

Each ride is a conditional write on its expected status (contract 6.2): a
driver accepting, or the rider cancelling, at the same moment wins or loses
cleanly, and a second run (another process) changes nothing.
"""

import logging

from ..repository import ride_repository, sms_repository
from ..utils import database
from . import ride_rules
from .ride_rules import AWAITING_PAYMENT, EXPIRED, PAYMENT_PAID, PAYMENT_REFUNDED, PENDING

logger = logging.getLogger(__name__)

EXPIRABLE_STATUSES = (AWAITING_PAYMENT, PENDING)


def expire_due_rides() -> int:
    """Expires every ride past its deadline. Returns how many expired."""
    now = ride_rules.now()
    expired = 0
    with database.session() as session:
        for ride in ride_repository.find_due(session, EXPIRABLE_STATUSES, now):
            previous_status = ride.status
            ride.status = EXPIRED
            ride.expired_at = now
            if ride.payment_status == PAYMENT_PAID:
                # Simulated (H10): with a real provider, the refund call follows the transaction.
                ride.payment_status = PAYMENT_REFUNDED
            if not ride_repository.update_if_status(session, ride, previous_status):
                # Accepted, paid or cancelled in between: it is no longer due.
                continue
            expired += 1
            no_driver = previous_status == PENDING
            logger.info(
                "Ride expired",
                extra={"context": {"rideId": ride.id, "reason": "no_driver" if no_driver else "not_paid"}},
            )
            if no_driver:
                sms_repository.send(
                    session, user_id=ride.rider_id, kind=sms_repository.RIDE_EXPIRED_NO_DRIVER, ride_id=ride.id
                )
    return expired
