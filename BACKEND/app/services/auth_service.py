"""
Authentication: registration of a rider, login, activation of an account
created by someone else, and the checks behind the session renewal.

The service decides who may log in; the HTTP side (cookies, tokens) is in
utils/access.py and the controller.
"""

import logging
from datetime import datetime, timezone

from ..repository import user_repository
from ..repository.user_repository import DuplicateValue, User
from ..utils import database
from ..utils.errors import Conflict, Forbidden, TooManyRequests, Unauthorized, UnprocessableEntity
from ..utils.passwords import hash_secret, verify_or_waste_time
from ..utils.rate_limit import AttemptLimiter
from .account_rules import ACTIVE, RIDER, SUSPENDED

logger = logging.getLogger(__name__)

MAX_FAILED_ATTEMPTS = 5
ATTEMPT_WINDOW_SECONDS = 15 * 60

# Separate counters: failing the login must not block the activation.
login_attempts = AttemptLimiter(MAX_FAILED_ATTEMPTS, ATTEMPT_WINDOW_SECONDS)
activation_attempts = AttemptLimiter(MAX_FAILED_ATTEMPTS, ATTEMPT_WINDOW_SECONDS)

PHONE_TAKEN = (
    "Ce numéro a déjà un compte. S'il a été créé par le centre d'appel, "
    "choisissez « J'ai reçu un code »."
)
EMAIL_TAKEN = "Cette adresse e-mail est déjà utilisée par un autre compte."
WRONG_CREDENTIALS = "Numéro ou mot de passe incorrect."
WRONG_CODE = "Code incorrect ou expiré. Demandez un nouveau code au centre d'appel."
TOO_MANY_ATTEMPTS = "Trop d'essais. Réessayez dans 15 minutes."
ACCOUNT_SUSPENDED = "Ce compte est suspendu. Contactez le centre d'appel."
SESSION_ENDED = "Votre session a pris fin. Reconnectez-vous."


def register_rider(
    *,
    first_name: str,
    last_name: str,
    phone: str,
    password: str,
    email: str | None,
    needs_accessible_vehicle: bool,
) -> User:
    """Creates an active rider account. Drivers, partners and staff are created by an administrator."""
    with database.session() as session:
        if user_repository.find_by_phone(session, phone) is not None:
            raise Conflict(PHONE_TAKEN)
        if email is not None and user_repository.email_taken(session, email):
            raise Conflict(EMAIL_TAKEN)
        try:
            user = user_repository.insert_user(
                session,
                User(
                    role=RIDER,
                    status=ACTIVE,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    email=email,
                    password_hash=hash_secret(password),
                    needs_accessible_vehicle=needs_accessible_vehicle,
                ),
            )
        except DuplicateValue:
            # Two registrations with the same number at the same moment.
            raise Conflict(PHONE_TAKEN) from None

    logger.info("Rider registered", extra={"context": {"userId": user.id}})
    return user


def login(phone: str, password: str) -> User:
    if login_attempts.is_blocked(phone):
        raise TooManyRequests(TOO_MANY_ATTEMPTS)

    with database.session() as session:
        user = user_repository.find_by_phone(session, phone)

    # An account not activated yet has no password: it fails like a wrong one.
    if not verify_or_waste_time(user.password_hash if user else None, password):
        login_attempts.record_failure(phone)
        logger.warning("Login failed", extra={"context": {"userId": user.id if user else None}})
        raise Unauthorized(WRONG_CREDENTIALS)

    if user.status == SUSPENDED:
        raise Forbidden(ACCOUNT_SUSPENDED)

    login_attempts.reset(phone)
    logger.info("Logged in", extra={"context": {"userId": user.id}})
    return user


def activate(phone: str, code: str, password: str) -> User:
    """First password of an account created by someone else, or new password after a forgotten one."""
    if activation_attempts.is_blocked(phone):
        raise TooManyRequests(TOO_MANY_ATTEMPTS)

    with database.session() as session:
        user = user_repository.find_by_phone(session, phone)
        code_still_valid = (
            user is not None
            and user.activation_code_expires_at is not None
            and user.activation_code_expires_at > datetime.now(timezone.utc)
        )
        code_hash = user.activation_code_hash if code_still_valid else None

        # One message whatever went wrong: it must not reveal whether the
        # number has an account, or a code.
        if not verify_or_waste_time(code_hash, code):
            activation_attempts.record_failure(phone)
            logger.warning("Activation failed", extra={"context": {"userId": user.id if user else None}})
            raise UnprocessableEntity(WRONG_CODE)

        if user.status == SUSPENDED:
            raise Forbidden(ACCOUNT_SUSPENDED)

        # Single use: the code is erased as soon as it has served.
        user.password_hash = hash_secret(password)
        user.activation_code_hash = None
        user.activation_code_expires_at = None
        user_repository.update_user(session, user)

    activation_attempts.reset(phone)
    logger.info("Account activated", extra={"context": {"userId": user.id}})
    return user


def session_user(user_id: int) -> User:
    """The account behind a valid token, as long as it may still use the app.

    Called at every session renewal and by GET /auth/me: this is where a
    suspended account loses access.
    """
    with database.session() as session:
        user = user_repository.find_by_id(session, user_id)
    if user is None or user.status == SUSPENDED or user.password_hash is None:
        raise Unauthorized(SESSION_ENDED)
    return user
