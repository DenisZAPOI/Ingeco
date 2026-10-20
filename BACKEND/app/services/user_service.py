"""
The logged-in user's own account: profile changes.

The phone number (the login), the role and the priority status are not
changed here: only an administrator does that.
"""

import logging
from dataclasses import dataclass

from ..repository import user_repository
from ..repository.user_repository import DuplicateValue, User
from ..utils import database
from ..utils.errors import Conflict, UnprocessableEntity
from ..utils.passwords import hash_secret, verify_secret
from .account_rules import RIDER
from .auth_service import EMAIL_TAKEN, session_user

logger = logging.getLogger(__name__)

WRONG_CURRENT_PASSWORD = "Le mot de passe actuel est incorrect."
RIDERS_ONLY = "Ce réglage ne concerne que les usagers."

# Marks a field the caller did not send: different from null, which empties it.
_UNCHANGED = object()


@dataclass
class ProfileChanges:
    first_name: str | object = _UNCHANGED
    last_name: str | object = _UNCHANGED
    email: str | None | object = _UNCHANGED
    needs_accessible_vehicle: bool | object = _UNCHANGED
    current_password: str | None = None
    new_password: str | None = None


def update_profile(user_id: int, changes: ProfileChanges) -> User:
    user = session_user(user_id)

    if changes.needs_accessible_vehicle is not _UNCHANGED and user.role != RIDER:
        raise UnprocessableEntity(RIDERS_ONLY)

    if changes.new_password is not None:
        # Asking for the current password: a phone left unlocked must not be
        # enough to take over the account.
        if changes.current_password is None or not verify_secret(user.password_hash, changes.current_password):
            raise UnprocessableEntity(WRONG_CURRENT_PASSWORD)
        user.password_hash = hash_secret(changes.new_password)

    for name in ("first_name", "last_name", "email", "needs_accessible_vehicle"):
        value = getattr(changes, name)
        if value is not _UNCHANGED:
            setattr(user, name, value)

    with database.session() as session:
        if user.email is not None and user_repository.email_taken(session, user.email, except_user_id=user.id):
            raise Conflict(EMAIL_TAKEN)
        try:
            user_repository.update_user(session, user)
        except DuplicateValue:
            raise Conflict(EMAIL_TAKEN) from None

    logger.info("Profile updated", extra={"context": {"userId": user.id}})
    return user
