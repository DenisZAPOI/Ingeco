"""The driver side: online, position, offers, then accept, release, start and complete (UC20 to UC27).

Chloé (account 3) drives an accessible vehicle. A second driver without one
is added here when a test needs two.
"""

from datetime import timedelta

import pytest

from app.repository import user_repository
from app.services import ride_rules
from app.utils import database
from tests.test_auth import DRIVER_PHONE, RIDER_PHONE, csrf_headers, login
from tests.test_rides import CAYENNE_TOWN_HALL, OPERATOR_PHONE, OTHER_RIDER_PHONE, book, booking, pay

SECOND_DRIVER_PHONE = "0694 00 00 09"
INES_ID = 9
# Near the town hall of Cayenne, and 15 km away (outside the 10 km of the offers).
NEAR_CAYENNE = {"lat": 4.9400, "lng": -52.3300}
FAR_AWAY = {"lat": 4.8000, "lng": -52.4200}


@pytest.fixture
def second_driver():
    """Inès, of sql/demo-data.sql: her vehicle is not accessible."""
    with database.session() as session:
        return user_repository.find_by_id(session, INES_ID)


def waiting_ride(client, phone=RIDER_PHONE, **changes) -> int:
    """A ride booked and paid by a rider: it waits for a driver."""
    login(client, phone=phone)
    ride_id = book(client, booking(**changes)).get_json()["id"]
    pay(client, ride_id)
    return ride_id


def scheduled_in(clock, **delta) -> str:
    return (clock.current + timedelta(**delta)).isoformat()


def go_online(client, phone=DRIVER_PHONE, available=True):
    login(client, phone=phone)
    return client.put("/drivers/me/availability", json={"isAvailable": available}, headers=csrf_headers(client))


def send_position(client, position=NEAR_CAYENNE):
    return client.put("/drivers/me/location", json=position, headers=csrf_headers(client))


def offers(client, kind="immediate"):
    return client.get("/drivers/me/ride-offers", query_string={"type": kind})


def offered_ids(client, kind="immediate") -> list[int]:
    return [offer["ride"]["id"] for offer in offers(client, kind).get_json()["items"]]


def act(client, ride_id, action):
    return client.post(f"/rides/{ride_id}/{action}", headers=csrf_headers(client))


# --- Online, position --------------------------------------------------------

def test_a_driver_goes_online_and_offline(client):
    assert go_online(client).get_json() == {"isAvailable": True}
    assert client.get("/auth/me").get_json()["isAvailable"] is True

    assert go_online(client, available=False).get_json() == {"isAvailable": False}
    assert client.get("/auth/me").get_json()["isAvailable"] is False


def test_going_offline_erases_the_position(client):
    go_online(client)
    send_position(client)

    go_online(client, available=False)

    with database.session() as session:
        assert user_repository.find_by_id(session, 3).location is None


def test_an_offline_driver_neither_sends_a_position_nor_sees_offers(client):
    login(client, phone=DRIVER_PHONE)

    assert send_position(client).status_code == 409
    assert offers(client).status_code == 409


def test_an_impossible_position_is_refused(client):
    go_online(client)

    assert send_position(client, {"lat": 91, "lng": 0}).status_code == 400


@pytest.mark.parametrize("phone", [RIDER_PHONE, OPERATOR_PHONE])
def test_only_a_driver_has_an_availability(client, phone):
    login(client, phone=phone)

    response = client.put("/drivers/me/availability", json={"isAvailable": True}, headers=csrf_headers(client))

    assert response.status_code == 403
    assert client.get("/auth/me").get_json()["isAvailable"] is None


# --- Offers ------------------------------------------------------------------

def test_immediate_offers_are_near_the_driver_nearest_first(client):
    farther = waiting_ride(client, pickup={**CAYENNE_TOWN_HALL, "lat": 4.9300, "lng": -52.3100})
    nearer = waiting_ride(client, phone=OTHER_RIDER_PHONE)
    go_online(client)
    send_position(client)

    response = offers(client).get_json()

    assert response["located"] is True
    assert [offer["ride"]["id"] for offer in response["items"]] == [nearer, farther]
    assert response["items"][0]["distanceToPickupKm"] < response["items"][1]["distanceToPickupKm"]


def test_a_ride_more_than_10_km_away_is_not_offered(client):
    waiting_ride(client)
    go_online(client)
    send_position(client, FAR_AWAY)

    assert offered_ids(client) == []


def test_without_a_recent_position_the_whole_zone_is_offered(client, clock):
    ride_id = waiting_ride(client)
    go_online(client)
    send_position(client, FAR_AWAY)
    clock.move(minutes=6)

    response = offers(client).get_json()

    assert response["located"] is False
    assert [offer["ride"]["id"] for offer in response["items"]] == [ride_id]
    assert response["items"][0]["distanceToPickupKm"] is None


def test_scheduled_offers_come_by_date_whatever_the_position(client, clock):
    later = waiting_ride(client, scheduledAt=scheduled_in(clock, days=2))
    sooner = waiting_ride(client, scheduledAt=scheduled_in(clock, days=1))
    waiting_ride(client)  # immediate: not in this tab
    go_online(client)
    send_position(client, FAR_AWAY)

    assert offered_ids(client, "scheduled") == [sooner, later]


def test_a_ride_needing_an_accessible_vehicle_is_offered_only_to_such_a_vehicle(client, second_driver):
    ride_id = waiting_ride(client, phone=OTHER_RIDER_PHONE)  # Bruno needs an accessible vehicle

    go_online(client, phone=SECOND_DRIVER_PHONE)
    assert offered_ids(client) == []
    assert act(client, ride_id, "accept").status_code == 409

    go_online(client)
    assert offered_ids(client) == [ride_id]


def test_an_offer_hides_the_rider(client):
    waiting_ride(client)
    go_online(client)

    ride = offers(client).get_json()["items"][0]["ride"]

    assert ride["rider"] is None


def test_a_ride_not_paid_or_past_its_time_is_not_offered(client, clock):
    login(client)
    book(client)  # awaiting payment
    paid = waiting_ride(client, phone=OTHER_RIDER_PHONE)
    go_online(client)
    clock.move(minutes=16)  # no driver in 15 minutes: expired (UC60 not done yet)

    assert offered_ids(client) == []
    assert act(client, paid, "accept").status_code == 409


# --- Accept ------------------------------------------------------------------

def test_accepting_a_ride_gives_each_one_the_other_s_contact(client):
    ride_id = waiting_ride(client)
    go_online(client)

    accepted = act(client, ride_id, "accept")

    assert accepted.status_code == 200
    ride = accepted.get_json()
    assert ride["status"] == "accepted"
    assert ride["rider"] == {"firstName": "Alice", "phone": "+594694000001"}
    assert ride["driver"] is None  # the driver knows themselves

    login(client)
    driver = client.get(f"/rides/{ride_id}").get_json()["driver"]
    assert driver["firstName"] == "Chloé"
    assert driver["phone"] == "+594694000003"
    assert driver["vehicle"] == {"plate": "AA-001-AA", "model": "Véhicule fictif", "isAccessible": True}
    assert driver["averageScore"] is None


def test_accepting_twice_is_not_an_error(client):
    ride_id = waiting_ride(client)
    go_online(client)
    act(client, ride_id, "accept")

    assert act(client, ride_id, "accept").status_code == 200


def test_a_ride_taken_by_another_driver_cannot_be_accepted(client, second_driver):
    ride_id = waiting_ride(client)
    go_online(client)
    act(client, ride_id, "accept")

    go_online(client, phone=SECOND_DRIVER_PHONE)
    response = act(client, ride_id, "accept")

    assert response.status_code == 409
    assert response.get_json()["detail"] == "Course déjà prise par un autre chauffeur."


def test_an_offline_driver_cannot_accept(client):
    ride_id = waiting_ride(client)
    login(client, phone=DRIVER_PHONE)

    assert act(client, ride_id, "accept").status_code == 409


def test_a_driver_holds_one_active_ride_at_a_time(client):
    first = waiting_ride(client)
    second = waiting_ride(client, phone=OTHER_RIDER_PHONE)
    go_online(client)
    act(client, first, "accept")

    response = act(client, second, "accept")

    assert response.status_code == 409
    assert "moins d'une heure" in response.get_json()["detail"]


def test_scheduled_rides_held_must_be_an_hour_apart(client, clock):
    at_ten = waiting_ride(client, scheduledAt=scheduled_in(clock, days=1))
    half_an_hour_later = waiting_ride(client, scheduledAt=scheduled_in(clock, days=1, minutes=30))
    two_hours_later = waiting_ride(client, scheduledAt=scheduled_in(clock, days=1, hours=2))
    go_online(client)
    act(client, at_ten, "accept")

    assert act(client, half_an_hour_later, "accept").status_code == 409
    assert act(client, two_hours_later, "accept").status_code == 200


def test_a_ride_scheduled_tomorrow_does_not_stop_an_immediate_one(client, clock):
    tomorrow = waiting_ride(client, scheduledAt=scheduled_in(clock, days=1))
    now = waiting_ride(client)
    go_online(client)
    act(client, tomorrow, "accept")

    assert act(client, now, "accept").status_code == 200


@pytest.mark.parametrize("phone", [RIDER_PHONE, OPERATOR_PHONE])
def test_only_a_driver_accepts(client, phone):
    ride_id = waiting_ride(client)
    login(client, phone=phone)

    assert act(client, ride_id, "accept").status_code == 403


# --- Release -----------------------------------------------------------------

def test_a_released_ride_is_offered_again_for_15_minutes(client, clock):
    ride_id = waiting_ride(client)
    go_online(client)
    act(client, ride_id, "accept")
    clock.move(minutes=10)

    ride = act(client, ride_id, "release").get_json()

    assert (ride["status"], ride["acceptedAt"], ride["rider"]) == ("pending", None, None)
    assert ride["paymentStatus"] == "paid"
    assert ride["expiresAt"].startswith((clock.current + ride_rules.DRIVER_SEARCH_DELAY).isoformat()[:16])
    assert offered_ids(client) == [ride_id]


def test_a_released_scheduled_ride_waits_until_its_time(client, clock):
    leaves_at = scheduled_in(clock, days=1)
    ride_id = waiting_ride(client, scheduledAt=leaves_at)
    go_online(client)
    act(client, ride_id, "accept")

    ride = act(client, ride_id, "release").get_json()

    assert ride["expiresAt"][:16] == ride["scheduledAt"][:16]


def test_releasing_again_says_the_ride_is_no_longer_theirs(client):
    ride_id = waiting_ride(client)
    go_online(client)
    act(client, ride_id, "accept")
    act(client, ride_id, "release")

    response = act(client, ride_id, "release")

    assert response.status_code == 409
    assert response.get_json()["detail"] == "Vous n'êtes plus le chauffeur de cette course."


def test_a_driver_cannot_release_the_ride_of_another(client, second_driver):
    ride_id = waiting_ride(client)
    go_online(client)
    act(client, ride_id, "accept")

    go_online(client, phone=SECOND_DRIVER_PHONE)

    assert act(client, ride_id, "release").status_code == 404


# --- Start, complete ---------------------------------------------------------

def test_a_ride_goes_from_accepted_to_completed_then_can_be_rated(client):
    ride_id = waiting_ride(client)
    go_online(client)
    act(client, ride_id, "accept")

    started = act(client, ride_id, "start").get_json()
    assert (started["status"], started["startedAt"] is not None) == ("in_progress", True)
    assert act(client, ride_id, "start").status_code == 200  # tapped twice

    completed = act(client, ride_id, "complete").get_json()
    assert (completed["status"], completed["rider"]) == ("completed", None)  # no more contact
    assert act(client, ride_id, "complete").status_code == 200

    login(client)
    rated = client.post(f"/rides/{ride_id}/rating", json={"score": 4}, headers=csrf_headers(client))
    assert rated.status_code == 201
    assert rated.get_json()["driver"]["averageScore"] == 4
    assert rated.get_json()["driver"]["phone"] is None


def test_a_ride_cannot_be_completed_before_it_starts(client):
    ride_id = waiting_ride(client)
    go_online(client)
    act(client, ride_id, "accept")

    assert act(client, ride_id, "complete").status_code == 409


def test_a_scheduled_ride_starts_at_the_earliest_an_hour_before(client, clock):
    ride_id = waiting_ride(client, scheduledAt=scheduled_in(clock, hours=3))
    go_online(client)
    act(client, ride_id, "accept")

    assert act(client, ride_id, "start").status_code == 409

    clock.move(hours=2, minutes=1)
    assert act(client, ride_id, "start").status_code == 200


def test_a_ride_cancelled_by_the_rider_cannot_be_started(client):
    ride_id = waiting_ride(client)
    go_online(client)
    act(client, ride_id, "accept")
    login(client)
    client.post(f"/rides/{ride_id}/cancel", headers=csrf_headers(client))

    login(client, phone=DRIVER_PHONE)

    assert act(client, ride_id, "start").status_code == 409


def test_a_started_ride_is_no_longer_cancellable_by_the_rider(client):
    ride_id = waiting_ride(client)
    go_online(client)
    act(client, ride_id, "accept")
    act(client, ride_id, "start")

    login(client)

    assert client.post(f"/rides/{ride_id}/cancel", headers=csrf_headers(client)).status_code == 409


# --- Who sees what -----------------------------------------------------------

def test_a_driver_sees_an_offer_but_not_another_driver_s_ride(client, second_driver):
    offered = waiting_ride(client)
    taken = waiting_ride(client, phone=OTHER_RIDER_PHONE)
    go_online(client)
    act(client, taken, "accept")

    go_online(client, phone=SECOND_DRIVER_PHONE)

    assert client.get(f"/rides/{offered}").status_code == 200
    assert client.get(f"/rides/{taken}").status_code == 404


def test_a_driver_lists_the_rides_they_hold(client):
    ride_id = waiting_ride(client)
    go_online(client)
    act(client, ride_id, "accept")

    upcoming = client.get("/rides", query_string={"when": "upcoming"}).get_json()["items"]

    assert [ride["id"] for ride in upcoming] == [ride_id]
    assert upcoming[0]["rider"]["firstName"] == "Alice"
