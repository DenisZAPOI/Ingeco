"""
Requests to delete an account: table demande_suppression of the DB team
(migration 002). One open request at most per account (computed column
`demande_en_cours`, unique). An administrator handles it by anonymising the
account (deletion_service); until then, the person may withdraw it.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from ..models import DeletionRequest, UserRow


@dataclass(frozen=True)
class OpenRequest:
    """An open request, with what the administrator needs to recognise the account."""

    user_id: int
    role: str
    first_name: str
    last_name: str
    phone: str
    requested_at: datetime


def find_open(session: Session, user_id: int) -> datetime | None:
    """When the account's open request was sent, or None."""
    return session.scalar(
        select(DeletionRequest.requested_at).where(
            DeletionRequest.user_id == user_id, DeletionRequest.handled_at.is_(None)
        )
    )


def add(session: Session, user_id: int, now: datetime) -> None:
    """Call it with the account locked (user_repository.lock) and after find_open():
    two taps at the same moment then make one request."""
    session.add(DeletionRequest(user_id=user_id, requested_at=now))
    session.flush()


def withdraw(session: Session, user_id: int) -> bool:
    """Removes the account's open request; False if there was none."""
    result = session.execute(
        delete(DeletionRequest).where(DeletionRequest.user_id == user_id, DeletionRequest.handled_at.is_(None))
    )
    return result.rowcount > 0  # type: ignore[attr-defined]


def list_open(session: Session) -> list[OpenRequest]:
    """The open requests, the oldest first: the first sent is the first handled."""
    rows = session.execute(
        select(DeletionRequest.user_id, DeletionRequest.requested_at, UserRow)
        .join(UserRow, UserRow.id == DeletionRequest.user_id)
        .where(DeletionRequest.handled_at.is_(None))
        .order_by(DeletionRequest.requested_at, DeletionRequest.id)
    )
    return [
        OpenRequest(
            user_id=user_id,
            role=user.role,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            requested_at=requested_at,
        )
        for user_id, requested_at, user in rows
    ]


def mark_handled(session: Session, user_id: int, admin_id: int, now: datetime) -> bool:
    """False if the account had no open request (withdrawn in between)."""
    result = session.execute(
        update(DeletionRequest)
        .where(DeletionRequest.user_id == user_id, DeletionRequest.handled_at.is_(None))
        .values(handled_at=now, handled_by_id=admin_id)
    )
    return result.rowcount > 0  # type: ignore[attr-defined]
