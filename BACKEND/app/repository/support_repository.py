"""
Help requests (module M0): table demande_aide of the DB team (migration 027,
issue #57). "Être rappelé" for now; "Signaler un problème" will use the same
table. An administrator or an operator marks a request handled; it is then
deleted after a while (retention_service, audit RGPD R4).
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from ..models import SupportRequestRow

_CALLBACK = "rappel"
_KIND_FROM_ROW = {"rappel": "callback", "signalement": "report"}


@dataclass(frozen=True)
class SupportRequest:
    id: int
    kind: str
    user_id: int | None
    phone: str | None
    message: str | None
    created_at: datetime
    handled_at: datetime | None


def add_callback(session: Session, user_id: int | None, phone: str, now: datetime) -> int:
    """A request to be called back at `phone`; `user_id` None for someone without an account."""
    row = SupportRequestRow(kind=_CALLBACK, user_id=user_id, phone=phone, created_at=now)
    session.add(row)
    session.flush()
    return row.id


def list_open_callbacks(session: Session) -> list[SupportRequest]:
    """The callbacks nobody handled yet, the oldest first."""
    rows = session.scalars(
        select(SupportRequestRow)
        .where(SupportRequestRow.kind == _CALLBACK, SupportRequestRow.handled_at.is_(None))
        .order_by(SupportRequestRow.created_at, SupportRequestRow.id)
    )
    return [_to_request(row) for row in rows]


def find_by_user(session: Session, user_id: int) -> list[SupportRequest]:
    """Every request of an account, the most recent first (« Mes données »)."""
    rows = session.scalars(
        select(SupportRequestRow)
        .where(SupportRequestRow.user_id == user_id)
        .order_by(SupportRequestRow.created_at.desc(), SupportRequestRow.id.desc())
    )
    return [_to_request(row) for row in rows]


def mark_handled(session: Session, request_id: int, staff_id: int, now: datetime) -> bool:
    """False if there is no such request, or it was handled already."""
    result = session.execute(
        update(SupportRequestRow)
        .where(SupportRequestRow.id == request_id, SupportRequestRow.handled_at.is_(None))
        .values(handled_at=now, handled_by_id=staff_id)
    )
    return result.rowcount > 0  # type: ignore[attr-defined]


def erase_texts_of(session: Session, user_id: int) -> None:
    """A deleted account: its messages and the numbers it gave go (migration 025)."""
    session.execute(
        update(SupportRequestRow).where(SupportRequestRow.user_id == user_id).values(message=None, phone=None)
    )


def delete_handled_before(session: Session, cutoff: datetime) -> int:
    """Deletes the requests handled before `cutoff`; returns how many."""
    result = session.execute(
        delete(SupportRequestRow).where(SupportRequestRow.handled_at < cutoff)
    )
    return result.rowcount  # type: ignore[attr-defined]


def _to_request(row: SupportRequestRow) -> SupportRequest:
    return SupportRequest(
        id=row.id,
        kind=_KIND_FROM_ROW[row.kind],
        user_id=row.user_id,
        phone=row.phone,
        message=row.message,
        created_at=row.created_at,
        handled_at=row.handled_at,
    )
