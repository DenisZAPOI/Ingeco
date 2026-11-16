"""
Communes of French Guiana (reference data of the DB team, table `commune`).

The table lists the 22 communes (migration 010); `desservie` says which ones
receive rides (H18, zones set by the administrator). A job offer or a help
service can be in a commune that is not served: its name is still needed.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Commune as CommuneRow


@dataclass(frozen=True)
class Commune:
    id: int
    name: str
    served: bool


def list_communes(session: Session, *, served_only: bool) -> list[Commune]:
    """Sorted by name, as the collation of the table compares them (accents, case)."""
    query = select(CommuneRow).order_by(CommuneRow.name)
    if served_only:
        query = query.where(CommuneRow.is_served.is_(True))
    return [_to_commune(row) for row in session.scalars(query)]


def find_by_id(session: Session, commune_id: int) -> Commune | None:
    """Served or not: the caller decides (a ride needs a served one)."""
    row = session.get(CommuneRow, commune_id)
    return _to_commune(row) if row else None


def _to_commune(row: CommuneRow) -> Commune:
    return Commune(id=row.id, name=row.name, served=row.is_served)
