"""
Limits and locks (audit F5, F6, F14, F15): the API cannot be saturated, nor
its address service quota used up, by one person or one machine.
"""

import threading
import time
from datetime import datetime, timedelta, timezone

from app.repository import ride_repository
from app.services import driver_service, place_service, ride_service, user_service
from app.services.auth_service import MAX_FAILED_ATTEMPTS, MAX_FAILED_ATTEMPTS_PER_ADDRESS
from app.services.ride_rules import MAX_OPEN_SCHEDULED_RIDES
from app.utils import passwords, rate_limit
from app.utils.rate_limit import AttemptLimiter
from tests.test_auth import DEV_PASSWORD, DRIVER_PHONE, RIDER_PHONE, csrf_headers, login
from tests.test_rides import OTHER_RIDER_PHONE, book, booking, pay

WRONG_PASSWORD = "Mauvais-1!"


def later(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


# --- Login: per network address, and the hashing (F5) ---------------------------

def test_one_address_trying_many_numbers_is_stopped(client):
    for number in range(MAX_FAILED_ATTEMPTS_PER_ADDRESS):
        assert login(client, phone=f"0694 70 00 {number:02d}", password=WRONG_PASSWORD).status_code == 401

    assert login(client, phone=RIDER_PHONE).status_code == 429


def test_another_address_still_logs_in(app, client):
    for number in range(MAX_FAILED_ATTEMPTS_PER_ADDRESS):
        login(client, phone=f"0694 70 00 {number:02d}", password=WRONG_PASSWORD)

    other_network = app.test_client()
    response = other_network.post(
        "/auth/login", json={"phone": RIDER_PHONE, "password": DEV_PASSWORD}, environ_base={"REMOTE_ADDR": "10.0.0.2"}
    )

    assert response.status_code == 200


def test_too_many_hashings_at_once_get_a_429(client, monkeypatch):
    busy = threading.BoundedSemaphore(1)
    busy.acquire()
    monkeypatch.setattr(passwords, "_hashing_slots", busy)
    monkeypatch.setattr(passwords, "HASH_WAIT_SECONDS", 0)

    response = login(client)

    assert response.status_code == 429
    assert response.get_json()["detail"] == passwords.BUSY


def test_the_limiter_counts_and_checks_in_one_step():
    limiter = AttemptLimiter(max_failures=1, window_seconds=60)

    assert limiter.try_record("key") is True
    assert limiter.try_record("key") is False
    limiter.cancel_last("key")
    assert limiter.try_record("key") is True


def test_the_limiter_forgets_the_old_keys(monkeypatch):
    now = [0.0]
    monkeypatch.setattr(rate_limit, "SWEEP_THRESHOLD", 3)
    limiter = AttemptLimiter(max_failures=5, window_seconds=60, clock=lambda: now[0])
    for key in ("a", "b", "c"):
        limiter.record_failure(key)

    now[0] = 120.0
    limiter.record_failure("d")

    assert limiter.key_count() == 1


# --- Current password (F14) -----------------------------------------------------

def test_the_current_password_cannot_be_guessed_without_end(client):
    login(client)

    def change(current):
        return client.patch(
            "/users/me", json={"currentPassword": current, "newPassword": "Nouveau-2026!"}, headers=csrf_headers(client)
        )

    for _ in range(MAX_FAILED_ATTEMPTS):
        assert change(WRONG_PASSWORD).status_code == 422

    assert change(DEV_PASSWORD).status_code == 429
    user_service.current_password_attempts.clear()


# --- Open rides of a rider (F6) -------------------------------------------------

def test_a_rider_has_one_immediate_ride_at_a_time(client):
    login(client)
    assert book(client).status_code == 201

    response = book(client)

    assert response.status_code == 422
    assert response.get_json()["detail"] == ride_service.TOO_MANY_IMMEDIATE


def test_a_cancelled_ride_frees_the_place(client):
    login(client)
    ride_id = book(client).get_json()["id"]
    client.post(f"/rides/{ride_id}/cancel", headers=csrf_headers(client))

    assert book(client).status_code == 201


def test_a_rider_has_three_scheduled_rides_at_most(client):
    login(client)
    for hours in range(1, MAX_OPEN_SCHEDULED_RIDES + 1):
        assert book(client, booking(scheduledAt=later(hours * 2))).status_code == 201
    assert book(client).status_code == 201  # an immediate one is still possible

    response = book(client, booking(scheduledAt=later(24)))

    assert response.status_code == 422
    assert response.get_json()["detail"] == ride_service.TOO_MANY_SCHEDULED


def test_the_limit_is_per_rider(client):
    login(client)
    book(client)

    login(client, phone=OTHER_RIDER_PHONE)

    assert book(client).status_code == 201


def test_a_retry_of_the_same_booking_is_not_counted(client):
    login(client)
    body = booking()
    book(client, body)

    assert book(client, body).status_code == 200


# --- Address service quota (F6) -------------------------------------------------

def test_searches_and_estimates_share_a_quota_per_account(client, monkeypatch):
    monkeypatch.setattr(place_service, "lookups", AttemptLimiter(2, 600))
    login(client)
    search = {"search": "mairie", "communeId": 1}
    estimate = {"pickup": booking()["pickup"], "dropoff": booking()["dropoff"]}

    assert client.get("/places", query_string=search).status_code == 200
    assert client.post("/rides/estimate", json=estimate, headers=csrf_headers(client)).status_code == 200

    assert client.get("/places", query_string=search).status_code == 429
    login(client, phone=OTHER_RIDER_PHONE)
    assert client.get("/places", query_string=search).status_code == 200


# --- Two acceptances of the same driver at the same moment (F15) ---------------

def test_a_driver_accepting_two_rides_at_once_gets_only_one(app, client, monkeypatch):
    login(client)
    first = book(client).get_json()["id"]
    pay(client, first)
    login(client, phone=OTHER_RIDER_PHONE)
    second = book(client).get_json()["id"]
    pay(client, second)
    driver = app.test_client()
    login(driver, phone=DRIVER_PHONE)
    driver.put("/drivers/me/availability", json={"isAvailable": True}, headers=csrf_headers(driver))

    # Widens the window between the timetable check and the write.
    original = ride_repository.find_driver_rides

    def slow(*args, **kwargs):
        rides = original(*args, **kwargs)
        time.sleep(0.2)
        return rides

    monkeypatch.setattr(ride_repository, "find_driver_rides", slow)
    codes = []

    def accept(ride_id):
        codes.append(driver.post(f"/rides/{ride_id}/accept", headers=csrf_headers(driver)).status_code)

    threads = [threading.Thread(target=accept, args=(ride_id,)) for ride_id in (first, second)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(codes) == [200, 409]
    assert len(ride_repository.find_driver_rides(None, 3, driver_service.ride_rules.HELD_STATUSES)) == 1
