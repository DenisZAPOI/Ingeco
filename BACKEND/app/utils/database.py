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

import logging
from collections.abc import Callable
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

logger = logging.getLogger(__name__)

# Key of session.info holding the actions to run once the transaction is committed.
_AFTER_COMMIT = "after_commit"


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
    # Only reached once the commit succeeded: a rollback never runs them.
    _run_after_commit(current_session)


def after_commit(current_session: Session, action: Callable[[], None]) -> None:
    """Runs `action` once the transaction of `current_session` is committed, never if it fails.

    For what must not be announced before it is saved: a real-time event
    emitted, then cancelled by a rollback, would tell of a state that never
    existed.
    """
    current_session.info.setdefault(_AFTER_COMMIT, []).append(action)


def _run_after_commit(committed_session: Session) -> None:
    for action in committed_session.info.pop(_AFTER_COMMIT, []):
        try:
            action()
        except Exception:
            # The write is saved: a failed announcement must not turn it into an error.
            logger.exception("Action after commit failed")
