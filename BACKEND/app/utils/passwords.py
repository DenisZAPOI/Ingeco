"""
Hashing of secrets: passwords and activation codes.

scrypt (through Werkzeug, already installed with Flask): a deliberately slow,
salted algorithm. A stolen hash cannot be reversed, and testing millions of
guesses costs too much. A secret is NEVER stored or logged in clear.
"""

import threading
from collections.abc import Callable
from typing import TypeVar

from werkzeug.security import check_password_hash, generate_password_hash

from .errors import TooManyRequests

_METHOD = "scrypt"

# Each scrypt costs about 110 ms of CPU and 32 MB of memory: a few dozen at the
# same time (logins with random numbers) would stop the API. Beyond this many
# at once, the request waits a little, then gets a 429.
MAX_CONCURRENT_HASHES = 4
HASH_WAIT_SECONDS = 5
BUSY = "Le service est très demandé. Réessayez dans quelques secondes."
_hashing_slots = threading.BoundedSemaphore(MAX_CONCURRENT_HASHES)

Result = TypeVar("Result")


def _in_a_slot(work: Callable[[], Result]) -> Result:
    if not _hashing_slots.acquire(timeout=HASH_WAIT_SECONDS):
        raise TooManyRequests(BUSY)
    try:
        return work()
    finally:
        _hashing_slots.release()


def hash_secret(secret: str) -> str:
    return _in_a_slot(lambda: generate_password_hash(secret, method=_METHOD))


def verify_secret(secret_hash: str, secret: str) -> bool:
    return _in_a_slot(lambda: check_password_hash(secret_hash, secret))


# Compared against when the account does not exist: the answer then takes as
# long as for a wrong password, so timing does not reveal which phone numbers
# have an account.
_DUMMY_HASH = generate_password_hash("no-account-with-this-number", method=_METHOD)


def verify_or_waste_time(secret_hash: str | None, secret: str) -> bool:
    """verify_secret, or the same amount of work against a dummy hash."""
    if secret_hash is None:
        verify_secret(_DUMMY_HASH, secret)
        return False
    return verify_secret(secret_hash, secret)
