"""Expiry of the rides left without a driver (UC60), and the periodic task that runs it.

The task is disabled in the tests: they move the clock, then run it themselves.
"""

import pytest

from app.services import expiry_service
from app.utils import periodic
from tests.test_auth import RIDER_PHONE, csrf_headers, login
from tests.test_drivers import go_online, scheduled_in, waiting_ride
from tests.test_rides import book, booking

RIDER_ID = 1  # Alice


def ride(client, ride_id):
    login(client, phone=RIDER_PHONE)
    return client.get(f"/rides/{ride_id}").get_json()


def unpaid_ride(client) -> int:
    login(client)
    return book(client, booking()).get_json()["id"]


def sms_lines(caplog):
    return [record for record in caplog.records if record.getMessage() == "SMS simulated"]


def test_an_unpaid_ride_expires_15_minutes_after_the_booking_without_sms(client, clock, caplog):
    ride_id = unpaid_ride(client)

    clock.move(minutes=14)
    assert expiry_service.expire_due_rides() == 0
    clock.move(minutes=2)
    assert expiry_service.expire_due_rides() == 1

    expired = ride(client, ride_id)
    assert (expired["status"], expired["paymentStatus"]) == ("expired", "pending")
    assert expired["expiredAt"] is not None
    assert sms_lines(caplog) == []


def test_a_paid_ride_without_driver_is_refunded_and_the_rider_told(client, clock, caplog):
    ride_id = waiting_ride(client)

    clock.move(minutes=16)
    expiry_service.expire_due_rides()

    expired = ride(client, ride_id)
    assert (expired["status"], expired["paymentStatus"]) == ("expired", "refunded")
    [sms] = sms_lines(caplog)
    assert sms.context == {"kind": "ride_expired_no_driver", "userId": RIDER_ID, "rideId": ride_id}
    # GDPR: neither the number nor any text of the message.
    assert "694" not in caplog.text


def test_a_scheduled_ride_waits_for_a_driver_until_its_time(client, clock):
    ride_id = waiting_ride(client, scheduledAt=scheduled_in(clock, hours=2))

    clock.move(minutes=119)
    expiry_service.expire_due_rides()
    assert ride(client, ride_id)["status"] == "pending"

    clock.move(minutes=2)
    expiry_service.expire_due_rides()
    assert ride(client, ride_id)["status"] == "expired"


def test_a_ride_taken_by_a_driver_never_expires(client, clock):
    ride_id = waiting_ride(client)
    go_online(client)
    client.post(f"/rides/{ride_id}/accept", headers=csrf_headers(client))

    clock.move(hours=2)
    expiry_service.expire_due_rides()

    assert ride(client, ride_id)["status"] == "accepted"


def test_a_second_run_changes_nothing_and_sends_no_second_sms(client, clock, caplog):
    waiting_ride(client)
    clock.move(minutes=16)

    assert expiry_service.expire_due_rides() == 1
    assert expiry_service.expire_due_rides() == 0
    assert len(sms_lines(caplog)) == 1


def test_an_expired_ride_is_in_the_past_rides_and_can_no_longer_be_paid_or_cancelled(client, clock):
    ride_id = unpaid_ride(client)
    clock.move(minutes=16)
    expiry_service.expire_due_rides()

    login(client)
    past = client.get("/rides?when=past").get_json()["items"]
    assert [item["id"] for item in past] == [ride_id]
    assert client.post(f"/rides/{ride_id}/payment", headers=csrf_headers(client)).status_code == 409
    assert client.post(f"/rides/{ride_id}/cancel", headers=csrf_headers(client)).status_code == 409


# ---------------------------------------------------------------------------
#  The periodic task
# ---------------------------------------------------------------------------

class _StopLoop(Exception):
    pass


class _FakeSocketIO:
    """Runs the loop at once, and stops it after `rounds` turns."""

    def __init__(self, rounds: int):
        self.rounds = rounds

    def sleep(self, _seconds):
        if self.rounds == 0:
            raise _StopLoop
        self.rounds -= 1

    def start_background_task(self, loop):
        with pytest.raises(_StopLoop):
            loop()


def test_a_failed_run_does_not_stop_the_next_ones(caplog):
    runs = []

    def task():
        runs.append(1)
        if len(runs) == 1:
            raise RuntimeError("database unreachable")

    periodic.start(_FakeSocketIO(rounds=3), "test_task", 60, task)

    assert len(runs) == 3
    assert "Periodic task failed" in caplog.text
