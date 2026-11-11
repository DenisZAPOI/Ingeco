"""Free rides for the rider (interview of 03/11/2026, docs/decisions.md).

The app only serves the client's own structure for now: the rider pays
nothing. The price is still computed and kept (driver's earnings), and the
simulated payment is not asked for.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.services import ride_rules
from tests.test_auth import csrf_headers, login
from tests.test_drivers import act, go_online, offered_ids, send_position
from tests.test_rides import book, booking, estimate, pay


@pytest.fixture(autouse=True)
def free_rides(monkeypatch):
    """The value of the app today (conftest.py sets the paying one for the other tests)."""
    monkeypatch.setattr(ride_rules, "RIDES_FREE_FOR_RIDERS", True)


def test_the_estimate_shows_the_price_and_nothing_to_pay(client):
    login(client)

    price = estimate(client).get_json()

    assert price["priceCents"] == 1848
    assert price["riderAmountCents"] == 0


def test_a_free_ride_waits_for_a_driver_at_once(client):
    """No payment step: the search for a driver starts with the booking."""
    login(client)

    ride = book(client).get_json()

    assert ride["status"] == "pending"
    assert ride["paymentStatus"] == "not_required"
    assert ride["priceCents"] == 1848
    assert ride["riderAmountCents"] == 0


def test_a_free_ride_has_nothing_to_pay(client):
    login(client)
    ride = book(client).get_json()

    response = pay(client, ride["id"])

    assert response.status_code == 409


def test_a_free_ride_is_offered_to_the_drivers_and_accepted(client):
    login(client)
    ride_id = book(client).get_json()["id"]

    go_online(client)
    send_position(client)

    assert ride_id in offered_ids(client)
    assert act(client, ride_id, "accept").status_code == 200


def test_a_free_ride_cancelled_is_not_refunded(client):
    """Nothing was paid: nothing to give back, and never "remboursé" on screen."""
    login(client)
    ride = book(client).get_json()

    cancelled = client.post(f"/rides/{ride['id']}/cancel", headers=csrf_headers(client)).get_json()

    assert cancelled["status"] == "cancelled"
    assert cancelled["paymentStatus"] == "not_required"


def test_a_scheduled_free_ride_waits_until_its_time(client):
    """Same deadline as a paid one: a driver can take it until it leaves."""
    login(client)
    leaves = (datetime.now(timezone.utc) + timedelta(days=1)).replace(microsecond=0)

    ride = book(client, booking(scheduledAt=leaves.isoformat())).get_json()

    assert ride["status"] == "pending"
    assert datetime.fromisoformat(ride["expiresAt"]) == leaves
