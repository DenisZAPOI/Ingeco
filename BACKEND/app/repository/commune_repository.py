"""
Served communes (reference data of the DB team, table `commune`).

FAKE DATA until the repositories switch to the database: the same rows as
sql/schema-mvp.sql. Only these communes are served (H18).
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session


@dataclass(frozen=True)
class Commune:
    id: int
    name: str


_COMMUNES = (
    Commune(id=1, name="Cayenne"),
    Commune(id=2, name="Rémire-Montjoly"),
    Commune(id=3, name="Matoury"),
)


def list_communes(_session: Session) -> list[Commune]:
    return sorted(_COMMUNES, key=lambda commune: commune.name)


def find_by_id(_session: Session, commune_id: int) -> Commune | None:
    return next((commune for commune in _COMMUNES if commune.id == commune_id), None)
