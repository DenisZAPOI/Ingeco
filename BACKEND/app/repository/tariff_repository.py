"""
The active tariff (reference data of the DB team, table `tarif`).

The amounts of sql/schema-mvp.sql are still to be set by the client: a new
tariff is a row for the DB team (the old one stays, rides keep theirs).
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import TariffRow


@dataclass(frozen=True)
class Tariff:
    id: int
    base_fare_cents: int
    per_km_cents: int


class NoActiveTariff(RuntimeError):
    """The table has no active tariff: no price can be computed (a data error, not the user's)."""


def active_tariff(session: Session) -> Tariff:
    """One tariff in the MVP (H8): the unique key on tarif_actif allows only one."""
    row = session.scalars(select(TariffRow).where(TariffRow.is_active.is_(True))).one_or_none()
    if row is None:
        raise NoActiveTariff("No active row in the table tarif.")
    return Tariff(id=row.id, base_fare_cents=row.base_fare_cents, per_km_cents=row.per_km_cents)
