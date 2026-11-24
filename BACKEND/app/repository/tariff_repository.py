"""
The active tariff (table `tarif`), set by the administrator (M9, US07).

A change is a new version, never an update: the old row stays, inactive, and
every ride keeps the tariff it was booked with (cahier des charges §7.4).
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import TariffRow


@dataclass(frozen=True)
class Tariff:
    id: int
    base_fare_cents: int
    per_km_cents: int
    created_at: datetime


class NoActiveTariff(RuntimeError):
    """The table has no active tariff: no price can be computed (a data error, not the user's)."""


def active_tariff(session: Session) -> Tariff:
    """One tariff in the MVP (H8): the unique key on tarif_actif allows only one."""
    row = session.scalars(select(TariffRow).where(TariffRow.is_active.is_(True))).one_or_none()
    if row is None:
        raise NoActiveTariff("No active row in the table tarif.")
    return _to_tariff(row)


def new_version(session: Session, *, base_fare_cents: int, per_km_cents: int, created_at: datetime) -> Tariff:
    """Deactivates the active tariff, then writes the new one, active.

    The active row is locked first (SELECT … FOR UPDATE, ADR 022): of two
    administrators saving at the same moment, the second waits, then replaces
    the first one's version, instead of breaking the "one active tariff" key.
    """
    active_rows = session.scalars(select(TariffRow).where(TariffRow.is_active.is_(True)).with_for_update()).all()
    for row in active_rows:
        row.is_active = False
    # Written before the insert: the unique key allows one active row at a time.
    session.flush()
    new_row = TariffRow(base_fare_cents=base_fare_cents, per_km_cents=per_km_cents, is_active=True, created_at=created_at)
    session.add(new_row)
    session.flush()
    return _to_tariff(new_row)


def _to_tariff(row: TariffRow) -> Tariff:
    return Tariff(
        id=row.id,
        base_fare_cents=row.base_fare_cents,
        per_km_cents=row.per_km_cents,
        created_at=row.created_at,
    )
