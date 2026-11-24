"""
Retention of the personal data (RGPD art. 5.1.e, audit RGPD R4), run once a
day by the API (utils/periodic.py).

The durations are provisional until the client validates them
(CHANGER_SELON_DECISION, docs/decisions.md):
- a help request: deleted 3 months after it was handled;
- a ride: a year after its end, its exact stops become their communes and
  its rating's comment goes (the statistics keep what they need).

The older questionnaires go as soon as a new one is filled
(orientation_repository.save), and a deleted account is anonymised at once
(deletion_service).

Each step only changes what was not changed yet: a second run, or another
process running it too, changes nothing.
"""

import logging
from dataclasses import dataclass
from datetime import timedelta

from ..repository import ride_repository, support_repository
from ..utils import database
from . import ride_rules

logger = logging.getLogger(__name__)

# CHANGER_SELON_DECISION: durations to validate with the client.
HELP_REQUEST_RETENTION = timedelta(days=90)
RIDE_STOPS_RETENTION = timedelta(days=365)
# Once a day is enough for durations counted in months.
PURGE_INTERVAL_SECONDS = 24 * 60 * 60


@dataclass(frozen=True)
class PurgeResult:
    help_requests_deleted: int
    rides_reduced: int


def purge() -> PurgeResult:
    now = ride_rules.now()
    with database.session() as session:
        help_requests_deleted = support_repository.delete_handled_before(session, now - HELP_REQUEST_RETENTION)
        rides_reduced = ride_repository.keep_only_communes(
            session, decimals=ride_rules.COMMUNE_ONLY_DECIMALS, finished_before=now - RIDE_STOPS_RETENTION
        )
    result = PurgeResult(help_requests_deleted=help_requests_deleted, rides_reduced=rides_reduced)
    logger.info(
        "Retention purge",
        extra={"context": {"helpRequestsDeleted": help_requests_deleted, "ridesReduced": rides_reduced}},
    )
    return result
