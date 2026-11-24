"""
Help requests (cahier des charges §6, module M0): "Être rappelé".

The human contact offered with every action plan (§7.1). Open to anyone, with
or without an account: someone of the structure calls back. No emergency
service is promised (§6).
"""

import logging

from ..repository import support_repository
from ..repository.support_repository import SupportRequest
from ..utils import database
from ..utils.errors import NotFound, TooManyRequests
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

NO_SUCH_CALLBACK = "Cette demande de rappel n'existe pas ou a déjà été traitée."

callbacks_by_address = AttemptLimiter(MAX_CALLBACKS_PER_ADDRESS, CALLBACK_WINDOW_SECONDS)


def request_callback(phone: str, user_id: int | None, client_address: str | None) -> None:
    """Records a request to be called back at `phone` (already normalized)."""
    if not callbacks_by_address.try_record(client_address or UNKNOWN_ADDRESS):
        raise TooManyRequests(TOO_MANY_CALLBACKS)
    with database.session() as session:
        request_id = support_repository.add_callback(session, user_id, phone, ride_rules.now())
    # Neither the number nor the account: personal data stays out of the logs.
    logger.info("Callback requested", extra={"context": {"request_id": request_id}})


def open_callbacks() -> list[SupportRequest]:
    """The callbacks to make, the oldest first (operator, administrator)."""
    with database.session() as session:
        return support_repository.list_open_callbacks(session)


def mark_callback_handled(*, staff_id: int, request_id: int) -> None:
    """Called back: the request leaves the list, and is deleted after a while (retention_service)."""
    with database.session() as session:
        handled = support_repository.mark_handled(session, request_id, staff_id, ride_rules.now())
    if not handled:
        raise NotFound(NO_SUCH_CALLBACK)
    logger.info("Callback handled", extra={"context": {"request_id": request_id, "byStaffId": staff_id}})
