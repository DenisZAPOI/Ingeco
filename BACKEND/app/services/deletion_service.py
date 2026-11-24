"""
Deleting an account (cahier des charges §6 P1, RGPD art. 17, audit RGPD R3).

The person asks from their profile; an administrator handles the request by
anonymising the account (decision of 03/11, migration 025): a person keeps
the hand, and no deletion happens by mistake from a shared phone. Until then,
the person may withdraw their request.

Anonymising keeps the account's id and its rides, for the statistics, without
anything that names the person: names, e-mail, phone, password, photo,
position, free texts, and the exact addresses of their rides (only the
communes stay).
"""

import logging
from datetime import datetime

from ..repository import (
    deletion_repository,
    orientation_repository,
    ride_repository,
    support_repository,
    user_repository,
)
from ..repository.deletion_repository import OpenRequest
from ..utils import database
from ..utils.errors import Conflict, NotFound
from . import ride_rules
from .account_rules import DELETED, DRIVER, RIDER
from .admin_service import ACCOUNT_NOT_FOUND, cancel_waiting_rides

logger = logging.getLogger(__name__)

NO_REQUEST = "Vous n'avez pas demandé la suppression de votre compte."
NO_OPEN_REQUEST = "Ce compte n'a pas de demande de suppression en cours."
RIDER_HAS_RIDE = (
    "Cet usager a un trajet accepté par un chauffeur ou en cours. "
    "Attendez qu'il soit terminé avant de supprimer son compte."
)
DRIVER_HAS_RIDE = (
    "Ce chauffeur a une course acceptée ou en cours. "
    "Attendez qu'elle soit terminée avant de supprimer son compte."
)


# --- The person --------------------------------------------------------------

def request_deletion(user_id: int) -> datetime:
    """Records the request; asking again returns the first one. Returns when it was sent."""
    with database.session() as session:
        # Two taps at the same moment make one request.
        user_repository.lock(session, user_id)
        requested_at = deletion_repository.find_open(session, user_id)
        if requested_at is not None:
            return requested_at
        requested_at = ride_rules.now()
        deletion_repository.add(session, user_id, requested_at)
    logger.info("Deletion requested", extra={"context": {"userId": user_id}})
    return requested_at


def deletion_requested_at(user_id: int) -> datetime:
    """When the open request was sent; NotFound without one."""
    with database.session() as session:
        requested_at = deletion_repository.find_open(session, user_id)
    if requested_at is None:
        raise NotFound(NO_REQUEST)
    return requested_at


def withdraw_request(user_id: int) -> None:
    """Withdraws the open request; withdrawing twice is not an error (a double tap)."""
    with database.session() as session:
        withdrawn = deletion_repository.withdraw(session, user_id)
    if withdrawn:
        logger.info("Deletion request withdrawn", extra={"context": {"userId": user_id}})


# --- The administrator -------------------------------------------------------

def list_requests() -> list[OpenRequest]:
    with database.session() as session:
        return deletion_repository.list_open(session)


def anonymise(*, admin_id: int, user_id: int) -> None:
    """Handles the open request of an account by anonymising it.

    A rider's rides no driver took yet are cancelled and refunded; a ride a
    driver holds (or a driver holding one) is refused: wait for its end.
    """
    with database.session() as session:
        user_repository.lock(session, user_id)
        user = user_repository.find_by_id(session, user_id)
        if user is None or user.status == DELETED:
            raise NotFound(ACCOUNT_NOT_FOUND)
        if deletion_repository.find_open(session, user_id) is None:
            raise Conflict(NO_OPEN_REQUEST)

        if user.role == RIDER:
            cancel_waiting_rides(session, admin_id, user, reason="deletion", refused=RIDER_HAS_RIDE)
        if user.role == DRIVER and ride_repository.find_driver_rides(session, user_id, ride_rules.HELD_STATUSES):
            raise Conflict(DRIVER_HAS_RIDE)

        now = ride_rules.now()
        user_repository.anonymise(session, user_id)
        support_repository.erase_texts_of(session, user_id)
        orientation_repository.erase_texts_of(session, user_id)
        ride_repository.erase_comments_of(session, user_id)
        if user.role == RIDER:
            # Their home and where they went: only the communes stay.
            ride_repository.keep_only_communes(
                session, decimals=ride_rules.COMMUNE_ONLY_DECIMALS, rider_id=user_id
            )
        deletion_repository.mark_handled(session, user_id, admin_id, now)

    logger.info("Account anonymised", extra={"context": {"userId": user_id, "byAdminId": admin_id}})
