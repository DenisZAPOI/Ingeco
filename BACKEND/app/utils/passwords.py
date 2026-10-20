"""
Hashing of secrets: passwords and activation codes.

scrypt (through Werkzeug, already installed with Flask): a deliberately slow,
salted algorithm. A stolen hash cannot be reversed, and testing millions of
guesses costs too much. A secret is NEVER stored or logged in clear.
"""

from werkzeug.security import check_password_hash, generate_password_hash

_METHOD = "scrypt"


def hash_secret(secret: str) -> str:
    return generate_password_hash(secret, method=_METHOD)


def verify_secret(secret_hash: str, secret: str) -> bool:
    return check_password_hash(secret_hash, secret)


# Compared against when the account does not exist: the answer then takes as
# long as for a wrong password, so timing does not reveal which phone numbers
# have an account.
_DUMMY_HASH = hash_secret("no-account-with-this-number")


def verify_or_waste_time(secret_hash: str | None, secret: str) -> bool:
    """verify_secret, or the same amount of work against a dummy hash."""
    if secret_hash is None:
        verify_secret(_DUMMY_HASH, secret)
        return False
    return verify_secret(secret_hash, secret)
