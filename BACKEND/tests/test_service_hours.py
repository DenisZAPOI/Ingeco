"""Service hours: a request outside them is refused with an explanation (cahier des charges §18, P1).

Slots are in local time of Cayenne (UTC-3); the API stores and receives UTC.
Monday 23/11/2026 is used as the reference day.
"""

from datetime import datetime, time, timedelta, timezone

from sqlalchemy import delete

from app.models import ServiceHoursRow
from app.repository.service_hours_repository import ServiceSlot
from app.services import service_hours_rules
from app.utils import database
from tests.test_auth import login
from tests.test_rides import book, booking, estimate

MONDAY, TUESDAY, SUNDAY = 1, 2, 7

# Monday 6 h – 12 h and 14 h – 20 h; Tuesday until midnight; closed on Sunday (no row).
WEEK = [
    ServiceSlot(MONDAY, time(6), time(12)),
    ServiceSlot(MONDAY, time(14), time(20)),
    ServiceSlot(TUESDAY, time(6), time(23, 59, 59)),
]


def cayenne(day: int, hour: int, minute: int = 0, second: int = 0) -> datetime:
    """A time of November 2026 in Cayenne, as an aware datetime in UTC (as the API holds it)."""
    local = datetime(2026, 11, day, hour, minute, second, tzinfo=timezone(timedelta(hours=-3)))
    return local.astimezone(timezone.utc)


# --- Rules -------------------------------------------------------------------

def test_a_time_inside_a_slot_is_open():
    assert service_hours_rules.is_open(WEEK, cayenne(23, 9, 30))


def test_both_ends_of_a_slot_are_included():
    assert service_hours_rules.is_open(WEEK, cayenne(23, 6))
    assert service_hours_rules.is_open(WEEK, cayenne(23, 20))
    assert not service_hours_rules.is_open(WEEK, cayenne(23, 20, 0, 1))


def test_the_lunch_break_is_closed():
    assert not service_hours_rules.is_open(WEEK, cayenne(23, 13))


def test_the_day_is_the_day_in_cayenne_not_in_utc():
    # Monday 22 h in Cayenne is already Tuesday 1 h in UTC: Monday's hours apply, closed.
    monday_evening = cayenne(23, 22)
    assert monday_evening.weekday() == 1  # Tuesday in UTC

    assert not service_hours_rules.is_open(WEEK, monday_evening)


def test_until_midnight_includes_the_last_minute():
    assert service_hours_rules.is_open(WEEK, cayenne(24, 23, 59, 30))


def test_a_day_without_slot_is_closed():
    assert not service_hours_rules.is_open(WEEK, cayenne(29, 10))


def test_the_message_gives_the_hours_of_that_day():
    message = service_hours_rules.closed_message(WEEK, cayenne(23, 13))

    assert message == "Le service fonctionne le lundi de 6 h à 12 h et de 14 h à 20 h. Choisissez une autre heure."


def test_the_message_says_midnight_and_minutes_as_spoken():
    slots = [ServiceSlot(TUESDAY, time(6, 30), time(23, 59, 59))]

    message = service_hours_rules.closed_message(slots, cayenne(24, 5))

    assert message == "Le service fonctionne le mardi de 6 h 30 à minuit. Choisissez une autre heure."


def test_the_message_of_a_closed_day_asks_for_another_day():
    message = service_hours_rules.closed_message(WEEK, cayenne(29, 10))

    assert message == "Le service est fermé le dimanche. Choisissez un autre jour."


# --- Estimate and booking ----------------------------------------------------

def set_week(slots: list[ServiceSlot]) -> None:
    """Replaces the hours of the test database (reset before each test)."""
    with database.session() as session:
        session.execute(delete(ServiceHoursRow))
        for slot in slots:
            session.add(ServiceHoursRow(weekday=slot.weekday, opens_at=slot.opens_at, closes_at=slot.closes_at))


def test_the_provisional_hours_refuse_nothing(client, clock):
    # sql/schema-mvp.sql opens every day, all day (decisions.md, point A).
    clock.current = cayenne(29, 3)
    login(client)

    assert estimate(client).status_code == 200


def test_an_immediate_ride_is_refused_when_the_service_is_closed(client, clock):
    set_week(WEEK)
    clock.current = cayenne(23, 13)
    login(client)

    response = book(client)

    assert response.status_code == 422
    assert response.get_json()["detail"].startswith("Le service fonctionne le lundi de 6 h à 12 h")


def test_the_estimate_already_refuses_a_closed_departure(client, clock):
    set_week(WEEK)
    clock.current = cayenne(23, 13)
    login(client)

    response = estimate(client)

    assert response.status_code == 422
    assert "lundi" in response.get_json()["detail"]


def test_the_departure_time_counts_not_the_time_of_the_request(client, clock):
    # Booked on Monday at 22 h, closed, for Tuesday at 7 h, open.
    set_week(WEEK)
    clock.current = cayenne(23, 22)
    login(client)
    tuesday_morning = cayenne(24, 7).isoformat()

    assert estimate(client, scheduled_at=tuesday_morning).status_code == 200
    assert book(client, booking(scheduledAt=tuesday_morning)).status_code == 201


def test_a_scheduled_ride_on_a_closed_day_is_refused(client, clock):
    set_week(WEEK)
    clock.current = cayenne(27, 10)
    login(client)
    sunday = cayenne(29, 10).isoformat()

    response = book(client, booking(scheduledAt=sunday))

    assert response.status_code == 422
    assert response.get_json()["detail"] == "Le service est fermé le dimanche. Choisissez un autre jour."
