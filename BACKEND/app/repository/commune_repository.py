"""
Served communes (reference data of the DB team, table `commune`).

Only these communes are served (H18). Adding Kourou is a row for the DB team,
nothing changes here.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Commune as CommuneRow


@dataclass(frozen=True)
class Commune:
    id: int
    name: str


def list_communes(session: Session) -> list[Commune]:
    """Sorted by name, as the collation of the table compares them (accents, case)."""
    rows = session.scalars(select(CommuneRow).order_by(CommuneRow.name))
    return [Commune(id=row.id, name=row.name) for row in rows]


def find_by_id(session: Session, commune_id: int) -> Commune | None:
    row = session.get(CommuneRow, commune_id)
    return Commune(id=row.id, name=row.name) if row else None
