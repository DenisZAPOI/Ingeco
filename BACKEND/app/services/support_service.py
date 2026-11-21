"""
Help requests (cahier des charges §6, module M0): "Être rappelé".

The human contact offered with every action plan (§7.1). Open to anyone, with
or without an account: someone of the structure calls back. No emergency
service is promised (§6).
"""

import logging

from ..repository import support_repository
from ..utils import database
from ..utils.errors import TooManyRequests
from ..utils.rate_limit import AttemptLimiter
from . import ride_rules

logger = logging.getLogger(__name__)

# Per network address: anyone may ask without an account, and each request is
# written in the database. Wide enough for an association whose visitors share
# one network.
MAX_CALLBACKS_PER_ADDRESS = 5
CALLBACK_WINDOW_SECONDS = 60 * 60
UNKNOWN_ADDRESS = "unknown"
TOO_MANY_CALLBACKS = (
    "Vous avez déjà demandé à être rappelé plusieurs fois. Un conseiller va vous appeler. "
    "Vous pourrez refaire une demande dans une heure."
)

callbacks_by_address = AttemptLimiter(MAX_CALLBACKS_PER_ADDRESS, CALLBACK_WINDOW_SECONDS)


def request_callback(phone: str, user_id: int | None, client_address: str | None) -> None:
    """Records a request to be called back at `phone` (already normalized)."""
    if not callbacks_by_address.try_record(client_address or UNKNOWN_ADDRESS):
        raise TooManyRequests(TOO_MANY_CALLBACKS)
    with database.session() as session:
        request_id = support_repository.add_callback(session, user_id, phone, ride_rules.now())
    # Neither the number nor the account: personal data stays out of the logs.
    logger.info("Callback requested", extra={"context": {"request_id": request_id}})
