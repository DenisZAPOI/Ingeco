"""
The settings of the administrator, put back after every test.

sql/demo-data.sql, loaded before each test, leaves the reference data alone
(service hours, served communes, tariff): a test that changes them would
change them for every test after it (a ride booked at 21 h refused because
an earlier test closed the service at 20 h). They are read once, as the DB
team's scripts load them, and written back after each test.
"""

from dataclasses import dataclass
from datetime import time

from sqlalchemy import delete, select, update

from app.models import Commune, ServiceHoursRow, TariffRow
from app.utils import database


@dataclass(frozen=True)
class Slot:
    weekday: int
    opens_at: time
    closes_at: time


@dataclass(frozen=True)
class ReferenceSettings:
    slots: list[Slot]
    served_commune_ids: set[int]
    active_tariff_id: int


def read() -> ReferenceSettings:
    with database.session() as session:
        slots = [Slot(row.weekday, row.opens_at, row.closes_at) for row in session.scalars(select(ServiceHoursRow))]
        served_ids = set(session.scalars(select(Commune.id).where(Commune.is_served.is_(True))))
        active_tariff_id = session.scalars(select(TariffRow.id).where(TariffRow.is_active.is_(True))).one()
    return ReferenceSettings(slots=slots, served_commune_ids=served_ids, active_tariff_id=active_tariff_id)


def restore(settings: ReferenceSettings) -> None:
    with database.session() as session:
        session.execute(delete(ServiceHoursRow))
        for slot in settings.slots:
            session.add(ServiceHoursRow(weekday=slot.weekday, opens_at=slot.opens_at, closes_at=slot.closes_at))

        served = Commune.id.in_(settings.served_commune_ids)
        session.execute(update(Commune).values(is_served=served).execution_options(synchronize_session=False))

        # The tariffs added by a test stay (a ride may still refer to one),
        # inactive. Deactivated first: one active tariff at a time (unique key).
        session.execute(update(TariffRow).values(is_active=False).execution_options(synchronize_session=False))
        original = update(TariffRow).where(TariffRow.id == settings.active_tariff_id).values(is_active=True)
        session.execute(original.execution_options(synchronize_session=False))
