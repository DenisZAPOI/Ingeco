"""Booking a ride: estimate, booking, simulated payment and detail (UC10 to UC12, UC14).

Fake places and distances (no ORS key in the tests, see conftest.py).
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.repository.place_repository import PlacesUnavailable
from app.services import ride_rules
from tests.test_auth import DRIVER_PHONE, csrf_headers, login

OTHER_RIDER_PHONE = "0694 00 00 02"  # Bruno, needs an accessible vehicle
OPERATOR_PHONE = "0694 00 00 05"

CAYENNE_TOWN_HALL = {"address": "Mairie de Cayenne", "lat": 4.9372, "lng": -52.3260, "communeId": 1}
MATOURY_TOWN_HALL = {"address": "Mairie de Matoury", "lat": 4.8470, "lng": -52.3310, "communeId": 3}
KOUROU = {"address": "Kourou", "lat": 5.1600, "lng": -52.6500, "communeId": 1}


def booking(**changes):
    body = {
        "clientRequestId": str(uuid.uuid4()),
        "purpose": "health",
        "pickup": CAYENNE_TOWN_HALL,
        "dropoff": MATOURY_TOWN_HALL,
        "scheduledAt": None,
    }
    return body | changes


def book(client, body=None):
    return client.post("/rides", json=body or booking(), headers=csrf_headers(client))


def estimate(client, pickup=CAYENNE_TOWN_HALL, dropoff=MATOURY_TOWN_HALL):
    return client.post("/rides/estimate", json={"pickup": pickup, "dropoff": dropoff}, headers=csrf_headers(client))


def pay(client, ride_id):
    return client.post(f"/rides/{ride_id}/payment", headers=csrf_headers(client))


@pytest.fixture
def clock(monkeypatch):
    """Moves the API's clock: clock.move(minutes=16)."""

    class Clock:
        current = datetime.now(timezone.utc)

        def move(self, **delta):
            self.current += timedelta(**delta)

    fake = Clock()
    monkeypatch.setattr(ride_rules, "now", lambda: fake.current)
    return fake


# --- Estimate ----------------------------------------------------------------

def test_the_estimate_is_the_pickup_fare_plus_the_price_per_kilometre(client):
    login(client)

    price = estimate(client).get_json()

    assert price["distanceKm"] == 13.1
    assert price["priceCents"] == 1848  # 800 + 80 × 13.1, provisional tariff of sql/schema-mvp.sql
    assert (price["voucherAmountCents"], price["riderAmountCents"]) == (0, price["priceCents"])


def test_a_trip_to_the_same_place_cannot_be_estimated(client):
    login(client)

    assert estimate(client, dropoff=CAYENNE_TOWN_HALL).status_code == 422


def test_a_position_far_from_the_pilot_zone_is_refused(client):
    login(client)

    response = estimate(client, dropoff=KOUROU)

    assert response.status_code == 422
    assert "Cayenne, Matoury et Rémire-Montjoly" in response.get_json()["detail"]


def test_without_road_distance_there_is_no_price(client, monkeypatch):
    def unavailable(*_positions):
        raise PlacesUnavailable("timeout")

    monkeypatch.setattr("app.services.ride_service.road_distance_km", unavailable)
    login(client)

    assert estimate(client).status_code == 503
    assert book(client).status_code == 503


def test_the_call_centre_may_estimate_but_a_driver_may_not(client):
    login(client, phone=OPERATOR_PHONE)
    assert estimate(client).status_code == 200

    login(client, phone=DRIVER_PHONE)
    assert estimate(client).status_code == 403


# --- Booking -----------------------------------------------------------------

def test_a_booked_ride_waits_for_the_payment_of_its_server_side_price(client, clock):
    login(client)

    response = book(client)

    assert response.status_code == 201
    ride = response.get_json()
    assert (ride["status"], ride["paymentStatus"], ride["channel"]) == ("awaiting_payment", "pending", "app")
    assert ride["priceCents"] == estimate(client).get_json()["priceCents"]
    assert datetime.fromisoformat(ride["expiresAt"]) == clock.current + timedelta(minutes=15)


def test_the_accessibility_need_is_copied_from_the_rider_profile(client):
    login(client, phone=OTHER_RIDER_PHONE)

    assert book(client).get_json()["needsAccessibleVehicle"] is True


def test_sending_the_same_booking_again_does_not_book_twice(client):
    login(client)
    body = booking()

    first = book(client, body)
    again = book(client, body)

    assert (first.status_code, again.status_code) == (201, 200)
    assert again.get_json()["id"] == first.get_json()["id"]


def test_a_booking_id_used_by_another_rider_is_refused(client):
    body = booking()
    login(client)
    book(client, body)

    login(client, phone=OTHER_RIDER_PHONE)

    assert book(client, body).status_code == 409


def test_a_scheduled_ride_must_leave_at_least_30_minutes_from_now(client, clock):
    login(client)
    too_soon = (clock.current + timedelta(minutes=20)).isoformat()
    later = (clock.current + timedelta(hours=2)).isoformat()

    refused = book(client, booking(scheduledAt=too_soon))
    accepted = book(client, booking(scheduledAt=later))

    assert refused.status_code == 400
    assert refused.get_json()["detail"]["fields"][0]["field"] == "scheduledAt"
    assert accepted.status_code == 201


def test_a_time_without_time_zone_is_refused(client):
    login(client)

    assert book(client, booking(scheduledAt="2030-01-01T10:00:00")).status_code == 400


def test_the_price_cannot_be_sent_by_the_phone(client):
    login(client)

    assert book(client, booking(priceCents=1)).status_code == 400


@pytest.mark.parametrize("phone", [DRIVER_PHONE, OPERATOR_PHONE])
def test_only_a_rider_books_for_themselves(client, phone):
    login(client, phone=phone)

    assert book(client).status_code == 403


def test_an_anonymous_caller_cannot_book(client):
    assert client.post("/rides", json=booking()).status_code == 401


# --- Payment -----------------------------------------------------------------

def test_once_paid_an_immediate_ride_waits_15_minutes_for_a_driver(client, clock):
    login(client)
    ride_id = book(client).get_json()["id"]
    clock.move(minutes=5)

    response = pay(client, ride_id)

    assert response.status_code == 200
    ride = response.get_json()
    assert (ride["status"], ride["paymentStatus"]) == ("pending", "paid")
    assert datetime.fromisoformat(ride["paidAt"]) == clock.current
    assert datetime.fromisoformat(ride["expiresAt"]) == clock.current + timedelta(minutes=15)


def test_once_paid_a_scheduled_ride_waits_for_a_driver_until_its_time(client, clock):
    login(client)
    scheduled_at = clock.current + timedelta(hours=3)
    ride_id = book(client, booking(scheduledAt=scheduled_at.isoformat())).get_json()["id"]

    ride = pay(client, ride_id).get_json()

    assert datetime.fromisoformat(ride["expiresAt"]) == scheduled_at


def test_paying_twice_is_not_an_error(client):
    login(client)
    ride_id = book(client).get_json()["id"]
    first = pay(client, ride_id).get_json()

    again = pay(client, ride_id)

    assert again.status_code == 200
    assert again.get_json()["paidAt"] == first["paidAt"]


def test_after_15_minutes_it_is_too_late_to_pay(client, clock):
    login(client)
    ride_id = book(client).get_json()["id"]
    clock.move(minutes=15)

    response = pay(client, ride_id)

    assert response.status_code == 409
    assert "15 minutes" in response.get_json()["detail"]


def test_a_rider_cannot_pay_the_ride_of_another(client):
    login(client)
    ride_id = book(client).get_json()["id"]

    login(client, phone=OTHER_RIDER_PHONE)

    assert pay(client, ride_id).status_code == 404


def test_the_call_centre_never_records_a_payment(client):
    login(client)
    ride_id = book(client).get_json()["id"]

    login(client, phone=OPERATOR_PHONE)

    assert pay(client, ride_id).status_code == 403


# --- Detail ------------------------------------------------------------------

def test_a_ride_is_seen_by_its_rider_and_the_call_centre_only(client):
    login(client)
    ride_id = book(client).get_json()["id"]
    assert client.get(f"/rides/{ride_id}").status_code == 200

    login(client, phone=OPERATOR_PHONE)
    assert client.get(f"/rides/{ride_id}").status_code == 200

    login(client, phone=OTHER_RIDER_PHONE)
    assert client.get(f"/rides/{ride_id}").status_code == 404

    login(client, phone=DRIVER_PHONE)
    assert client.get(f"/rides/{ride_id}").status_code == 404


def test_an_unknown_ride_is_not_found(client):
    login(client)

    assert client.get("/rides/999").status_code == 404
