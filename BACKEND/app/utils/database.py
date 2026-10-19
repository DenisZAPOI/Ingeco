"""
Database access.

The database belongs to the DB team (parcours C): this repo NEVER creates or
alters a table. ORM models describe tables that already exist, so
`Base.metadata.create_all()` is never called.

Mixed approach, one rule to decide:
  - the query fits in one readable ORM line → ORM;
  - three joins or a subtle condition → explicit SQL in repository/.

In both cases the SQLAlchemy session is the only entry point.
"""

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Parent class of every ORM model (see models/)."""


_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None

_NOT_INITIALIZED = "The database is not initialized: database.initialize(...) must be called at startup."


def initialize(database_url: str) -> Engine:
    """Creates the connection engine. Called once, at startup."""
    global _engine, _session_factory

    # pool_pre_ping: checks a connection is alive before reusing it, which
    # avoids errors after a network cut or a database restart.
    _engine = create_engine(database_url, pool_pre_ping=True)
    _session_factory = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)
    return _engine


def engine() -> Engine:
    if _engine is None:
        raise RuntimeError(_NOT_INITIALIZED)
    return _engine


@contextmanager
def session() -> Iterator[Session]:
    """Opens a session, commits on exit, rolls back on error.

    Every write goes through here. The transaction covers the whole block:
    a multi-step operation (book a ride and consume a voucher) succeeds or
    fails as a whole, never halfway.
    """
    if _session_factory is None:
        raise RuntimeError(_NOT_INITIALIZED)

    current_session = _session_factory()
    try:
        yield current_session
        current_session.commit()
    except Exception:
        current_session.rollback()
        raise
    finally:
        current_session.close()
