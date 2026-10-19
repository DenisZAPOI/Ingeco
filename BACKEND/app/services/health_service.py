"""
Diagnostic service.

The service layer holds the rules and drives the repository. It knows nothing
about Flask, HTTP or status codes.
"""

import logging
from dataclasses import dataclass

from ..repository import health_repository
from ..utils import database

logger = logging.getLogger(__name__)


class DatabaseUnreachable(Exception):
    """The database does not answer, or the connection is misconfigured."""


@dataclass(frozen=True)
class DatabaseState:
    dialect: str


def database_state() -> DatabaseState:
    """Queries the database. Raises DatabaseUnreachable if it does not answer."""
    try:
        with database.session() as session:
            health_repository.ping(session)
            return DatabaseState(dialect=health_repository.dialect(session))
    except Exception as error:
        # The technical detail goes to the logs, never to the response:
        # it would expose the host, the port and the driver.
        logger.error("Database unreachable", extra={"context": {"error": str(error)}})
        raise DatabaseUnreachable from error
