"""
Database access for the diagnostic.

Example of the "hand-written SQL" side of the mixed approach.
"""

from sqlalchemy import text
from sqlalchemy.orm import Session


def ping(session: Session) -> bool:
    """Full round trip with the database: fails if it is down."""
    return session.execute(text("SELECT 1")).scalar_one() == 1


def dialect(session: Session) -> str:
    """Database engine in use (sqlite, postgresql…), until the DB team picks one."""
    return session.get_bind().dialect.name
