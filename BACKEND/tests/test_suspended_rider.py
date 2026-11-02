"""
The rides of a rider being suspended (UC51): those not taken yet are
cancelled and refunded, one taken by a driver blocks the suspension.
"""

from datetime import datetime, timedelta, timezone

from app.repository import ride_repository
from app.services.admin_service import RIDER_HAS_RIDE
from tests.test_auth import ADMIN_PHONE, RIDER_PHONE, csrf_headers, login
from tests.test_drivers import act, go_online
from tests.test_rides import OPERATOR_PHONE, book, booking, pay

RIDER_ID = 1  # Alice
ADMIN_ID = 6


def suspend(client, user_id=RIDER_ID):
    login(client, phone=ADMIN_PHONE)
    return client.patch(f"/admin/users/{user_id}", json={"status": "suspended"}, headers=csrf_headers(client))


def ride(ride_id):
    return ride_repository.find_by_id(None, ride_id)


def sms_kinds(caplog):
    return [record.context["kind"] for record in caplog.records if record.getMessage() == "SMS simulated"]


def later(hours):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def test_the_rides_not_taken_yet_are_cancelled_and_refunded(client, caplog):
    login(client, phone=RIDER_PHONE)
    unpaid = book(client).get_json()["id"]
    scheduled = book(client, booking(scheduledAt=later(3))).get_json()["id"]
    pay(client, scheduled)

    response = suspend(client)

    assert response.status_code == 200
    assert response.get_json()["status"] == "suspended"
    assert (ride(unpaid).status, ride(unpaid).payment_status) == ("cancelled", "pending")
    assert (ride(scheduled).status, ride(scheduled).payment_status) == ("cancelled", "refunded")
    assert ride(scheduled).cancelled_by_id == ADMIN_ID
    assert sms_kinds(caplog) == ["suspended_rides_cancelled"]


def test_a_cancelled_ride_is_no_longer_offered(client):
    login(client, phone=RIDER_PHONE)
    waiting = book(client).get_json()["id"]
    pay(client, waiting)

    suspend(client)

    go_online(client)
    assert act(client, waiting, "accept").status_code == 409


def test_a_ride_accepted_by_a_driver_blocks_the_suspension(client):
    login(client, phone=RIDER_PHONE)
    taken = book(client).get_json()["id"]
    pay(client, taken)
    scheduled = book(client, booking(scheduledAt=later(3))).get_json()["id"]
    go_online(client)
    act(client, taken, "accept")

    response = suspend(client)

    assert response.status_code == 409
    assert response.get_json()["detail"] == RIDER_HAS_RIDE
    # Nothing changed: neither the account nor its other rides.
    assert client.get(f"/admin/users/{RIDER_ID}").get_json()["status"] == "active"
    assert ride(scheduled).status == "awaiting_payment"


def test_a_started_ride_blocks_the_suspension(client):
    login(client, phone=RIDER_PHONE)
    started = book(client).get_json()["id"]
    pay(client, started)
    go_online(client)
    act(client, started, "accept")
    act(client, started, "start")

    assert suspend(client).status_code == 409


def test_a_rider_without_ride_gets_no_sms(client, caplog):
    assert suspend(client).status_code == 200
    assert sms_kinds(caplog) == []


def test_the_finished_rides_are_left_as_they_are(client):
    login(client, phone=RIDER_PHONE)
    cancelled = book(client).get_json()["id"]
    client.post(f"/rides/{cancelled}/cancel", headers=csrf_headers(client))

    suspend(client)

    assert ride(cancelled).cancelled_by_id == RIDER_ID


def test_the_call_centre_cannot_suspend(client):
    login(client, phone=OPERATOR_PHONE)

    response = client.patch(f"/admin/users/{RIDER_ID}", json={"status": "suspended"}, headers=csrf_headers(client))

    assert response.status_code == 403
