"""
Administration of the accounts: list and search (UC51), create a driver, an
operator or an administrator (UC52), suspend, reactivate, mark a rider as
priority, change a vehicle (UC51), the driver's photo, and the activation
code (UC53).

Partner referents come with the vouchers (step 5): their structure is not in
the MVP schema yet.
"""

import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..repository import ride_repository, user_repository
from ..repository.user_repository import DuplicateValue, Position, User, Vehicle
from ..utils import database
from ..utils.errors import Conflict, NotFound, UnprocessableEntity
from ..utils.passwords import hash_secret
from . import account_rules, ride_rules
from .account_rules import ACTIVATION_CODE_LENGTH, ACTIVATION_CODE_VALIDITY_HOURS, ACTIVE, DRIVER, RIDER, SUSPENDED
from .auth_service import EMAIL_TAKEN

logger = logging.getLogger(__name__)

PAGE_SIZE = 20

ACCOUNT_NOT_FOUND = "Compte introuvable."
PHONE_TAKEN = "Ce numéro a déjà un compte. Cherchez-le dans la liste des comptes."
PLATE_TAKEN = "Cette immatriculation est déjà celle d'un autre chauffeur."
VEHICLE_REQUIRED = "Indiquez le véhicule du chauffeur."
DRIVERS_ONLY = "Seul un chauffeur a un véhicule et une photo."
RIDERS_ONLY = "Seul un usager peut être prioritaire."
NOT_YOURSELF = "Vous ne pouvez pas suspendre votre propre compte."
DRIVER_HAS_RIDE = (
    "Ce chauffeur a une course acceptée ou en cours. Attendez qu'elle soit terminée, "
    "ou annulez-la, avant de suspendre son compte."
)

# The photo is reduced by the browser (~15 KB) before it is sent: well
# beyond that, it was not reduced.
PHOTO_MAX_BYTES = 100 * 1024
_JPEG_START = b"\xff\xd8\xff"
NOT_A_JPEG = "La photo doit être une image JPEG."
PHOTO_TOO_LARGE = "La photo est trop lourde. Reprenez-la depuis l'écran du compte."
NO_PHOTO = "Ce chauffeur n'a pas encore de photo."

# Marks a field the caller did not send.
_UNCHANGED = object()


@dataclass(frozen=True)
class AccountPage:
    users: list[User]
    # Where the next page starts; None on the last page.
    next_position: Position | None


@dataclass(frozen=True)
class ActivationCode:
    # In clear only in this answer: shown once, never stored nor logged.
    code: str
    expires_at: datetime


@dataclass
class AccountChanges:
    status: str | object = _UNCHANGED
    is_priority: bool | object = _UNCHANGED
    vehicle: Vehicle | object = _UNCHANGED


# --- List (UC51) -------------------------------------------------------------

def list_accounts(*, search: str | None, role: str | None, status: str | None, after: Position | None) -> AccountPage:
    """A page of accounts, the newest first. `search`: a phone number (its start) or a name (contained)."""
    phone_prefix = account_rules.phone_prefix(search) if search else None
    name = search if search and phone_prefix is None else None
    with database.session() as session:
        # One more than the page: tells whether there is a next page, without counting.
        users = user_repository.find_page(
            session, name=name, phone_prefix=phone_prefix, role=role, status=status, after=after, limit=PAGE_SIZE + 1
        )
    if len(users) <= PAGE_SIZE:
        return AccountPage(users=users, next_position=None)
    last = users[PAGE_SIZE - 1]
    return AccountPage(users=users[:PAGE_SIZE], next_position=Position(created_at=last.created_at, user_id=last.id))


def get_account(user_id: int) -> User:
    with database.session() as session:
        return _find(session, user_id)


# --- Creation (UC52) ---------------------------------------------------------

def create_account(
    *,
    admin_id: int,
    role: str,
    first_name: str,
    last_name: str,
    phone: str,
    email: str | None,
    vehicle: Vehicle | None,
) -> tuple[User, ActivationCode]:
    """A driver (with their vehicle), an operator or an administrator, without password.

    The activation code comes with it: the administrator hands it over, the
    person chooses their password with POST /auth/activate.
    """
    if role == DRIVER and vehicle is None:
        raise UnprocessableEntity(VEHICLE_REQUIRED)
    if role != DRIVER and vehicle is not None:
        raise UnprocessableEntity(DRIVERS_ONLY)

    code, code_hash, expires_at = _new_code()
    user = User(
        role=role,
        status=ACTIVE,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
        vehicle=vehicle,
        activation_code_hash=code_hash,
        activation_code_expires_at=expires_at,
    )
    with database.session() as session:
        _check_free(session, user)
        try:
            user = user_repository.insert_user(session, user)
        except DuplicateValue:
            # Two creations with the same number (or plate) at the same moment.
            raise Conflict(PHONE_TAKEN) from None

    logger.info("Account created", extra={"context": {"userId": user.id, "role": role, "byAdminId": admin_id}})
    return user, ActivationCode(code=code, expires_at=expires_at)


# --- Changes (UC51) ----------------------------------------------------------

def update_account(*, admin_id: int, user_id: int, changes: AccountChanges) -> User:
    """Suspends or reactivates, marks a rider as priority, changes a driver's vehicle."""
    with database.session() as session:
        user = _find(session, user_id)

        if changes.is_priority is not _UNCHANGED:
            if user.role != RIDER:
                raise UnprocessableEntity(RIDERS_ONLY)
            user.is_priority = changes.is_priority

        if changes.vehicle is not _UNCHANGED:
            if user.role != DRIVER:
                raise UnprocessableEntity(DRIVERS_ONLY)
            user.vehicle = changes.vehicle

        if changes.status == SUSPENDED and user.status != SUSPENDED:
            _suspend(session, admin_id, user)
        elif changes.status == ACTIVE:
            user.status = ACTIVE

        _check_free(session, user)
        try:
            user_repository.update_user(session, user)
        except DuplicateValue:
            raise Conflict(PLATE_TAKEN) from None

    logger.info(
        "Account updated",
        extra={"context": {"userId": user.id, "status": user.status, "byAdminId": admin_id}},
    )
    return user


def _suspend(session, admin_id: int, user: User) -> None:
    """A suspended account cannot log in any more; a driver also goes offline.

    It loses access at the latest when its 15-minute token ends. A driver
    holding a ride is refused: the rider would wait for nobody.
    """
    if user.id == admin_id:
        raise UnprocessableEntity(NOT_YOURSELF)
    if user.role == DRIVER:
        if ride_repository.find_driver_rides(session, user.id, ride_rules.HELD_STATUSES):
            raise Conflict(DRIVER_HAS_RIDE)
        # Offline erases the position too (GDPR, H6).
        user.is_available = False
        user.location = None
    user.status = SUSPENDED


# --- Photo of a driver -------------------------------------------------------

def save_photo(*, admin_id: int, user_id: int, image: bytes) -> User:
    """Saves or replaces the face photo of a driver, taken at the in-person check."""
    if not image.startswith(_JPEG_START):
        raise UnprocessableEntity(NOT_A_JPEG)
    if len(image) > PHOTO_MAX_BYTES:
        raise UnprocessableEntity(PHOTO_TOO_LARGE)
    with database.session() as session:
        user = _find(session, user_id)
        if user.role != DRIVER:
            raise UnprocessableEntity(DRIVERS_ONLY)
        user_repository.save_photo(session, user_id, image, ride_rules.now())
        user = user_repository.find_by_id(session, user_id)
    logger.info("Driver photo saved", extra={"context": {"userId": user_id, "byAdminId": admin_id}})
    return user


def get_photo(user_id: int) -> tuple[bytes, datetime]:
    with database.session() as session:
        user = _find(session, user_id)
        image = user_repository.find_photo(session, user_id)
    if image is None or user.photo_updated_at is None:
        raise NotFound(NO_PHOTO)
    return image, user.photo_updated_at


# --- Activation code (UC53) --------------------------------------------------

def new_activation_code(*, admin_id: int, user_id: int) -> ActivationCode:
    """First access or forgotten password: a new code, valid 48 h, that replaces the previous one."""
    code, code_hash, expires_at = _new_code()
    with database.session() as session:
        user = _find(session, user_id)
        user.activation_code_hash = code_hash
        user.activation_code_expires_at = expires_at
        user_repository.update_user(session, user)
    # Never the code itself (it would open the account).
    logger.info("Activation code issued", extra={"context": {"userId": user_id, "byAdminId": admin_id}})
    return ActivationCode(code=code, expires_at=expires_at)


# --- Helpers -----------------------------------------------------------------

def _new_code() -> tuple[str, str, datetime]:
    """8 random digits, easy to dictate; only their hash is stored."""
    code = "".join(secrets.choice("0123456789") for _ in range(ACTIVATION_CODE_LENGTH))
    expires_at = ride_rules.now() + timedelta(hours=ACTIVATION_CODE_VALIDITY_HOURS)
    return code, hash_secret(code), expires_at


def _find(session, user_id: int) -> User:
    user = user_repository.find_by_id(session, user_id)
    if user is None:
        raise NotFound(ACCOUNT_NOT_FOUND)
    return user


def _check_free(session, user: User) -> None:
    """A readable message before the unique constraint answers."""
    other = user_repository.find_by_phone(session, user.phone)
    if other is not None and other.id != user.id:
        raise Conflict(PHONE_TAKEN)
    if user.email is not None and user_repository.email_taken(session, user.email, except_user_id=user.id):
        raise Conflict(EMAIL_TAKEN)
    if user.vehicle is not None and user_repository.plate_taken(session, user.vehicle.plate, except_user_id=user.id):
        raise Conflict(PLATE_TAKEN)
