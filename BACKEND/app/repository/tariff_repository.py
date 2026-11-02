"""
The active tariff (reference data of the DB team, table `tarif`).

FAKE DATA until the repositories switch to the database: the same row as
sql/schema-mvp.sql, whose amounts are still to be set by the client.
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session


@dataclass(frozen=True)
class Tariff:
    id: int
    base_fare_cents: int
    per_km_cents: int


_ACTIVE_TARIFF = Tariff(id=1, base_fare_cents=800, per_km_cents=80)


def active_tariff(_session: Session) -> Tariff:
    """One tariff in the MVP (H8)."""
    return _ACTIVE_TARIFF
