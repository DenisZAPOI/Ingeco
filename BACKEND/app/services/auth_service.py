"""
Authentication: registration of a rider (proven by an SMS code), login,
activation of an account created by someone else, forgotten password by SMS
code, and the checks behind the session renewal.

The service decides who may log in; the HTTP side (cookies, tokens) is in
utils/access.py and the controller.
"""

import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from ..repository import registration_repository, sms_repository, user_repository
from ..repository.registration_repository import PendingRegistration
from ..repository.user_repository import DuplicateValue, User
from ..utils import database
from ..utils.errors import Conflict, Forbidden, TooManyRequests, Unauthorized, UnprocessableEntity
from ..utils.passwords import hash_secret, verify_or_waste_time
from ..utils.rate_limit import AttemptLimiter
from .account_rules import ACTIVATION_CODE_LENGTH, ACTIVE, ADMIN, REGISTRATION_CODE_LENGTH, RIDER, SUSPENDED

logger = logging.getLogger(__name__)

MAX_FAILED_ATTEMPTS = 5
ATTEMPT_WINDOW_SECONDS = 15 * 60

# Separate counters: failing the login must not block the activation.
login_attempts = AttemptLimiter(MAX_FAILED_ATTEMPTS, ATTEMPT_WINDOW_SECONDS)
activation_attempts = AttemptLimiter(MAX_FAILED_ATTEMPTS, ATTEMPT_WINDOW_SECONDS)
# Per network address (audit F5): wide, for an association whose members share
# one connection, but one machine can no longer try numbers without end.
MAX_FAILED_ATTEMPTS_PER_ADDRESS = 30
login_attempts_by_address = AttemptLimiter(MAX_FAILED_ATTEMPTS_PER_ADDRESS, ATTEMPT_WINDOW_SECONDS)
activation_attempts_by_address = AttemptLimiter(MAX_FAILED_ATTEMPTS_PER_ADDRESS, ATTEMPT_WINDOW_SECONDS)
UNKNOWN_ADDRESS = "unknown"

# --- Registration by SMS code (audit F4) -------------------------------------
REGISTRATION_CODE_VALIDITY = timedelta(minutes=10)
# Codes sent: per number (a person retrying) and per network address (one
# machine trying many numbers). An association sharing one connection
# registers several people an hour without reaching it.
MAX_CODES_PER_PHONE = 3
MAX_CODES_PER_ADDRESS = 10
CODE_WINDOW_SECONDS = 60 * 60
registration_codes_by_phone = AttemptLimiter(MAX_CODES_PER_PHONE, CODE_WINDOW_SECONDS)
registration_codes_by_address = AttemptLimiter(MAX_CODES_PER_ADDRESS, CODE_WINDOW_SECONDS)
# With LOAD_DEMO_DATA, the code is always this one (README, part "Comptes de
# test"): the SMS are only simulated. Otherwise, random.
DEMO_REGISTRATION_CODE = "123456"
_demo_codes = False

# --- Forgotten password by SMS code (cahier des charges, §6 and §18) ---------
# The code goes in the activation code's columns: /auth/activate then sets the
# new password. Shorter than the 48 h of a code handed over by the team, since
# anyone can ask for one.
PASSWORD_RESET_CODE_VALIDITY = timedelta(minutes=15)
password_reset_codes_by_phone = AttemptLimiter(MAX_CODES_PER_PHONE, CODE_WINDOW_SECONDS)
password_reset_codes_by_address = AttemptLimiter(MAX_CODES_PER_ADDRESS, CODE_WINDOW_SECONDS)
# Same as the development accounts' activation code (README, "Comptes de test").
DEMO_PASSWORD_RESET_CODE = "12345678"

PHONE_TAKEN = (
    "Ce numéro a déjà un compte. S'il a été créé par le centre d'appel, "
    "choisissez « J'ai reçu un code »."
)
EMAIL_TAKEN = "Cette adresse e-mail est déjà utilisée par un autre compte."
EMAIL_TAKEN_AT_REGISTRATION = (
    "Cette adresse e-mail est déjà utilisée par un autre compte. "
    "Recommencez l'inscription avec une autre adresse, ou sans adresse."
)
WRONG_REGISTRATION_CODE = "Code incorrect ou expiré. Vérifiez le numéro, puis demandez un nouveau code."
TOO_MANY_CODES = "Trop de codes demandés. Réessayez dans une heure."
WRONG_CREDENTIALS = "Numéro ou mot de passe incorrect."
WRONG_CODE = (
    "Code incorrect ou expiré. Demandez un nouveau code avec « Mot de passe oublié », "
    "ou au centre d'appel."
)
TOO_MANY_ATTEMPTS = "Trop d'essais. Réessayez dans 15 minutes."
ACCOUNT_SUSPENDED = "Ce compte est suspendu. Contactez le centre d'appel."
SESSION_ENDED = "Votre session a pris fin. Reconnectez-vous."


def configure(*, demo_codes: bool) -> None:
    """Called once at startup: demo_codes with LOAD_DEMO_DATA (fixed registration code)."""
    global _demo_codes
    _demo_codes = demo_codes


@dataclass(frozen=True)
class CodeSent:
    expires_at: datetime


def start_registration(
    *,
    first_name: str,
    last_name: str,
    phone: str,
    password: str,
    email: str | None,
    needs_accessible_vehicle: bool,
    client_address: str | None,
) -> CodeSent:
    """Sends the SMS code that proves the phone. Nothing is created before it is typed.

    The same answer whether the number has an account or not, in the same
    time (both hashes are always computed): the API does not tell who uses
    the service. The SMS itself tells the holder of an existing account.
    Drivers, partners and staff are created by an administrator.
    """
    _count_attempt(registration_codes_by_phone, phone, registration_codes_by_address, client_address, TOO_MANY_CODES)

    code = DEMO_REGISTRATION_CODE if _demo_codes else _random_code()
    now = datetime.now(timezone.utc)
    registration = PendingRegistration(
        phone=phone,
        first_name=first_name,
        last_name=last_name,
        email=email,
        needs_accessible_vehicle=needs_accessible_vehicle,
        password_hash=hash_secret(password),
        code_hash=hash_secret(code),
        expires_at=now + REGISTRATION_CODE_VALIDITY,
    )
    with database.session() as session:
        if user_repository.find_by_phone(session, phone) is not None:
            # Nothing stored: the code typed then fails like a wrong one.
            sms_repository.send_to_number(session, phone=phone, kind=sms_repository.ALREADY_REGISTERED)
        else:
            registration_repository.save(session, registration, now)
            sms_repository.send_to_number(session, phone=phone, kind=sms_repository.REGISTRATION_CODE, code=code)
    return CodeSent(expires_at=registration.expires_at)


def confirm_registration(phone: str, code: str) -> User:
    """Creates the active rider account once the SMS code is right.

    5 wrong codes erase the registration: a new code must be asked for.
    """
    with database.session() as session:
        registration = registration_repository.find(session, phone)
        still_valid = registration is not None and registration.expires_at > datetime.now(timezone.utc)
        if not verify_or_waste_time(registration.code_hash if still_valid else None, code):
            if registration_repository.record_failure(session, phone) >= MAX_FAILED_ATTEMPTS:
                registration_repository.delete(session, phone)
            raise UnprocessableEntity(WRONG_REGISTRATION_CODE)
        registration_repository.delete(session, phone)

        # The phone is proven: saying now that an e-mail is taken reveals
        # nothing to someone who does not hold that phone.
        if registration.email is not None and user_repository.email_taken(session, registration.email):
            raise Conflict(EMAIL_TAKEN_AT_REGISTRATION)
        try:
            user = user_repository.insert_user(
                session,
                User(
                    role=RIDER,
                    status=ACTIVE,
                    first_name=registration.first_name,
                    last_name=registration.last_name,
                    phone=phone,
                    email=registration.email,
                    password_hash=registration.password_hash,
                    needs_accessible_vehicle=registration.needs_accessible_vehicle,
                ),
            )
        except DuplicateValue:
            # An account was created for this number since the code was sent.
            raise Conflict(PHONE_TAKEN) from None

    logger.info("Rider registered", extra={"context": {"userId": user.id}})
    return user


def start_password_reset(phone: str, client_address: str | None) -> CodeSent:
    """Sends by SMS an 8-digit code to type in /auth/activate with a new password.

    Same answer, in the same time, whatever the number: no account, an
    administrator, a suspended account. None of them gets an SMS. An
    administrator's account opens everything, so a stolen SIM card must not be
    enough: another administrator issues their code. The code replaces the
    previous one, including a code handed over by the team.
    """
    _count_attempt(
        password_reset_codes_by_phone, phone, password_reset_codes_by_address, client_address, TOO_MANY_CODES
    )

    code = DEMO_PASSWORD_RESET_CODE if _demo_codes else _random_code(ACTIVATION_CODE_LENGTH)
    code_hash = hash_secret(code)  # always computed: the answer time says nothing
    expires_at = datetime.now(timezone.utc) + PASSWORD_RESET_CODE_VALIDITY
    with database.session() as session:
        user = user_repository.find_by_phone(session, phone)
        if user is not None and user.status == ACTIVE and user.role != ADMIN:
            user.activation_code_hash = code_hash
            user.activation_code_expires_at = expires_at
            user_repository.update_user(session, user)
            sms_repository.send_to_number(session, phone=phone, kind=sms_repository.PASSWORD_RESET_CODE, code=code)
            logger.info("Password reset code sent", extra={"context": {"userId": user.id}})
    return CodeSent(expires_at=expires_at)


def _random_code(length: int = REGISTRATION_CODE_LENGTH) -> str:
    return "".join(secrets.choice("0123456789") for _ in range(length))


def _count_attempt(
    by_phone: AttemptLimiter, phone: str, by_address: AttemptLimiter, client_address: str | None, refusal: str
) -> None:
    """Counts the attempt BEFORE the costly hashing, or refuses it (429).

    Counted first and taken back on success: parallel requests cannot all
    pass the check before any of them is counted (audit F15).
    """
    address = client_address or UNKNOWN_ADDRESS
    if not by_phone.try_record(phone):
        raise TooManyRequests(refusal)
    if not by_address.try_record(address):
        by_phone.cancel_last(phone)
        raise TooManyRequests(refusal)


def _attempt_succeeded(by_phone: AttemptLimiter, phone: str, by_address: AttemptLimiter, client_address: str | None) -> None:
    by_phone.reset(phone)
    # Only this attempt: one right password must not wipe the failures of the
    # other numbers tried from the same address.
    by_address.cancel_last(client_address or UNKNOWN_ADDRESS)


def login(phone: str, password: str, client_address: str | None = None) -> User:
    _count_attempt(login_attempts, phone, login_attempts_by_address, client_address, TOO_MANY_ATTEMPTS)

    with database.session() as session:
        user = user_repository.find_by_phone(session, phone)

    # An account not activated yet has no password: it fails like a wrong one.
    if not verify_or_waste_time(user.password_hash if user else None, password):
        logger.warning("Login failed", extra={"context": {"userId": user.id if user else None}})
        raise Unauthorized(WRONG_CREDENTIALS)

    if user.status == SUSPENDED:
        raise Forbidden(ACCOUNT_SUSPENDED)

    _attempt_succeeded(login_attempts, phone, login_attempts_by_address, client_address)
    logger.info("Logged in", extra={"context": {"userId": user.id}})
    return user


def activate(phone: str, code: str, password: str, client_address: str | None = None) -> User:
    """First password of an account created by someone else, or new password after a forgotten one."""
    _count_attempt(activation_attempts, phone, activation_attempts_by_address, client_address, TOO_MANY_ATTEMPTS)

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
            logger.warning("Activation failed", extra={"context": {"userId": user.id if user else None}})
            raise UnprocessableEntity(WRONG_CODE)

        if user.status == SUSPENDED:
            raise Forbidden(ACCOUNT_SUSPENDED)

        # Single use: the code is erased as soon as it has served. A new
        # password ends the sessions opened with the old one.
        user.password_hash = hash_secret(password)
        user.session_version += 1
        user.activation_code_hash = None
        user.activation_code_expires_at = None
        user_repository.update_user(session, user)

    _attempt_succeeded(activation_attempts, phone, activation_attempts_by_address, client_address)
    logger.info("Account activated", extra={"context": {"userId": user.id}})
    return user


def session_user(user_id: int) -> User:
    """The account of the caller, as long as it may still use the app."""
    with database.session() as session:
        user = user_repository.find_by_id(session, user_id)
    if user is None or user.status == SUSPENDED or user.password_hash is None:
        raise Unauthorized(SESSION_ENDED)
    return user


def check_session(user_id: int, session_version: int | None) -> User:
    """The account behind a valid token, checked at EVERY request and renewal.

    This is where a suspended account, or a session opened before the last
    password change, loses access at once. A token without version (issued
    before versions existed) is refused like an old one.
    """
    user = session_user(user_id)
    if session_version != user.session_version:
        raise Unauthorized(SESSION_ENDED)
    return user
