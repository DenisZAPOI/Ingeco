"""
Is the service open at the time of a ride? (cahier des charges §18, P1: a
request outside the service hours is refused WITH an explanation.)

Pure functions, without the database: the slots are read by the caller. The
time compared is the DEPARTURE time (decided on 24/11/2026): now for an
immediate ride, the chosen time for a scheduled one. A ride can then be
booked in the evening for the next morning.

Slots are in local time of Cayenne (America/Cayenne, UTC-3 all year), both
ends included: 23:59:59 means "until midnight".
"""

from datetime import datetime, time

from ..repository.service_hours_repository import ServiceSlot
from .ride_rules import GUYANA_TIME

# 1 = Monday … 7 = Sunday (ISO 8601), as in the table.
DAY_NAMES = {1: "lundi", 2: "mardi", 3: "mercredi", 4: "jeudi", 5: "vendredi", 6: "samedi", 7: "dimanche"}

# The table writes "until midnight" as 23:59:59 (both ends included).
END_OF_DAY = time(23, 59, 59)


def is_open(slots: list[ServiceSlot], departure: datetime) -> bool:
    """True if `departure` (an aware datetime) falls in a slot of its day in Cayenne."""
    local = _local(departure)
    local_time = local.time()
    for slot in _slots_of_day(slots, local.isoweekday()):
        if slot.opens_at <= local_time <= slot.closes_at:
            return True
    return False


def closed_message(slots: list[ServiceSlot], departure: datetime) -> str:
    """Why the service refuses this departure, in plain words: the hours of that day."""
    weekday = _local(departure).isoweekday()
    day_name = DAY_NAMES[weekday]
    day_slots = _slots_of_day(slots, weekday)
    if not day_slots:
        return f"Le service est fermé le {day_name}. Choisissez un autre jour."
    ranges = " et ".join(f"de {_spoken_time(slot.opens_at)} à {_spoken_time(slot.closes_at)}" for slot in day_slots)
    return f"Le service fonctionne le {day_name} {ranges}. Choisissez une autre heure."


def _local(moment: datetime) -> datetime:
    # To the second, like the TIME columns: 20:00:00.4 is still 20:00:00.
    return moment.astimezone(GUYANA_TIME).replace(microsecond=0)


def _slots_of_day(slots: list[ServiceSlot], weekday: int) -> list[ServiceSlot]:
    day_slots = [slot for slot in slots if slot.weekday == weekday]
    return sorted(day_slots, key=lambda slot: slot.opens_at)


def _spoken_time(moment: time) -> str:
    """6 h, 6 h 30, minuit: as the hours are said, not 06:00:00."""
    if moment >= END_OF_DAY:
        return "minuit"
    if moment.minute == 0:
        return f"{moment.hour} h"
    return f"{moment.hour} h {moment.minute:02d}"
