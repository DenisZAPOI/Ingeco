"""Small helpers shared by the tests."""

from collections.abc import Callable
from typing import TypeVar

from sqlalchemy.orm import Session

from app.utils import database

T = TypeVar("T")


def in_session(read: Callable[[Session], T]) -> T:
    """Runs a repository read in its own transaction, as a service does."""
    with database.session() as session:
        return read(session)
