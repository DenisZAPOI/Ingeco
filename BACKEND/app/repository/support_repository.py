"""
Help requests (module M0): table demande_aide of the DB team (migration 027,
issue #57). "Être rappelé" for now; "Signaler un problème" will use the same
table. A request is never deleted: an administrator or an operator marks it
handled.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from ..models import SupportRequestRow

_CALLBACK = "rappel"


def add_callback(session: Session, user_id: int | None, phone: str, now: datetime) -> int:
    """A request to be called back at `phone`; `user_id` None for someone without an account."""
    row = SupportRequestRow(kind=_CALLBACK, user_id=user_id, phone=phone, created_at=now)
    session.add(row)
    session.flush()
    return row.id
