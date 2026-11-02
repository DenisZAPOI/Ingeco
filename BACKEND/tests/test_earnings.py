"""The driver's earnings (UC28): completed rides per day, in Guyana time.

Rides are driven for real (booked, paid, accepted, started, completed) with
the clock set to chosen moments.
"""

from datetime import datetime, timezone

import pytest

from tests.test_auth import ADMIN_PHONE, RIDER_PHONE, login
from tests.test_drivers import SECOND_DRIVER_PHONE, act, go_online, second_driver, waiting_ride  # noqa: F401 (fixture)

PRICE_CENTS = 1848  # Cayenne town hall to Matoury town hall, provisional tariff


def completed_ride(client, clock, completed_at: datetime, phone=None) -> int:
    """A ride booked, then taken and completed by Chloé (or `phone`) at `completed_at`."""
    clock.current = completed_at
    ride_id = waiting_ride(client)
    go_online(client, **({"phone": phone} if phone else {}))
    for action in ("accept", "start", "complete"):
        assert act(client, ride_id, action).status_code == 200
    return ride_id


def earnings(client, first_day, last_day, phone=None):
    login(client, **({"phone": phone} if phone else {"phone": "0694 00 00 03"}))
    return client.get(f"/drivers/me/earnings?from={first_day}&to={last_day}")


def utc(day, hour, minute=0):
    return datetime(2026, 11, day, hour, minute, tzinfo=timezone.utc)


def test_completed_rides_are_summed_per_day_the_most_recent_first(client, clock):
    completed_ride(client, clock, utc(2, 14))
    completed_ride(client, clock, utc(2, 18))
    completed_ride(client, clock, utc(4, 12))

    result = earnings(client, "2026-11-02", "2026-11-08").get_json()

    assert result["totalCents"] == 3 * PRICE_CENTS
    assert result["rideCount"] == 3
    assert result["days"] == [
        {"day": "2026-11-04", "rideCount": 1, "totalCents": PRICE_CENTS},
        {"day": "2026-11-02", "rideCount": 2, "totalCents": 2 * PRICE_CENTS},
    ]


def test_a_ride_counts_on_its_day_in_guyana_not_in_utc(client, clock):
    # 01:30 UTC on 3 November is 22:30 on 2 November in Cayenne.
    completed_ride(client, clock, utc(3, 1, 30))

    assert [day["day"] for day in earnings(client, "2026-11-02", "2026-11-02").get_json()["days"]] == ["2026-11-02"]
    assert earnings(client, "2026-11-03", "2026-11-03").get_json()["rideCount"] == 0


def test_the_first_and_last_days_are_included(client, clock):
    completed_ride(client, clock, utc(1, 3, 1))  # 00:01 on 1 November in Cayenne
    completed_ride(client, clock, utc(1, 2, 59))  # 23:59 on 31 October in Cayenne

    assert earnings(client, "2026-11-01", "2026-11-01").get_json()["rideCount"] == 1
    assert earnings(client, "2026-10-31", "2026-11-01").get_json()["rideCount"] == 2


def test_only_the_drivers_own_completed_rides_count(client, clock, second_driver):
    completed_ride(client, clock, utc(2, 14), phone=SECOND_DRIVER_PHONE)
    # Accepted but not completed.
    clock.current = utc(2, 15)
    ride_id = waiting_ride(client)
    go_online(client)
    act(client, ride_id, "accept")

    result = earnings(client, "2026-11-02", "2026-11-02").get_json()

    assert (result["rideCount"], result["totalCents"], result["days"]) == (0, 0, [])


@pytest.mark.parametrize(
    ("first_day", "last_day"),
    [("2026-11-08", "2026-11-02"), ("2026-10-01", "2026-11-01"), ("2026-11-02", "pas-une-date")],
)
def test_a_reversed_too_long_or_invalid_period_is_refused(client, first_day, last_day):
    assert earnings(client, first_day, last_day).status_code == 400


def test_a_period_of_a_whole_month_is_accepted(client):
    assert earnings(client, "2026-10-01", "2026-10-31").status_code == 200


@pytest.mark.parametrize("phone", [RIDER_PHONE, ADMIN_PHONE])
def test_only_a_driver_sees_earnings(client, phone):
    assert earnings(client, "2026-11-02", "2026-11-02", phone=phone).status_code == 403
