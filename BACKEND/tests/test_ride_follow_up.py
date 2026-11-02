"""After the booking: the rider's lists (UC17), cancellation (UC16) and rating (UC18).

The driver side does not exist yet: a ride is taken or finished here by
writing it in the repository, as a driver's action will.
"""

from datetime import timedelta

import pytest

from app.repository import ride_repository
from app.services import ride_rules
from tests.test_auth import DRIVER_PHONE, csrf_headers, login
from tests.test_rides import OPERATOR_PHONE, OTHER_RIDER_PHONE, book, booking, pay

DRIVER_ID = 3  # Chloé, development account
ADMIN_PHONE = "0694 00 00 06"


def booked_ride(client, **changes) -> int:
    return book(client, booking(**changes)).get_json()["id"]


def paid_ride(client) -> int:
    ride_id = booked_ride(client)
    pay(client, ride_id)
    return ride_id


def move_to(ride_id: int, status: str) -> None:
    """What the driver side will do: take, start or finish the ride."""
    ride = ride_repository.find_by_id(None, ride_id)
    previous = ride.status
    ride.status = status
    if status in (ride_rules.ACCEPTED, ride_rules.IN_PROGRESS, ride_rules.COMPLETED):
        ride.driver_id = DRIVER_ID
        ride.accepted_at = ride_rules.now()
    if status in (ride_rules.IN_PROGRESS, ride_rules.COMPLETED):
        ride.started_at = ride_rules.now()
    if status == ride_rules.COMPLETED:
        ride.completed_at = ride_rules.now()
    assert ride_repository.update_if_status(None, ride, previous)


def finished_ride(client) -> int:
    ride_id = paid_ride(client)
    move_to(ride_id, ride_rules.COMPLETED)
    return ride_id


def list_rides(client, when, cursor=None):
    query = {"when": when} | ({"cursor": cursor} if cursor else {})
    return client.get("/rides", query_string=query)


def ids(response) -> list[int]:
    return [ride["id"] for ride in response.get_json()["items"]]


def cancel(client, ride_id):
    return client.post(f"/rides/{ride_id}/cancel", headers=csrf_headers(client))


def rate(client, ride_id, score=5, comment=None):
    return client.post(
        f"/rides/{ride_id}/rating", json={"score": score, "comment": comment}, headers=csrf_headers(client)
    )


# --- Lists -------------------------------------------------------------------

def test_upcoming_rides_come_soonest_first_and_past_ones_most_recent_first(client, clock):
    login(client)
    later = booked_ride(client, scheduledAt=(clock.current + timedelta(days=2)).isoformat())
    sooner = booked_ride(client, scheduledAt=(clock.current + timedelta(days=1)).isoformat())
    first_finished = finished_ride(client)
    clock.move(minutes=1)
    last_finished = finished_ride(client)

    assert ids(list_rides(client, "upcoming")) == [sooner, later]
    past = list_rides(client, "past").get_json()
    assert [ride["id"] for ride in past["items"]] == [last_finished, first_finished]
    assert past["nextCursor"] is None


def test_past_rides_come_by_pages_of_20_without_repeat(client, clock):
    login(client)
    created = []
    for _ in range(ride_rules.PAST_PAGE_SIZE + 3):
        clock.move(minutes=1)
        created.append(finished_ride(client))

    first = list_rides(client, "past").get_json()
    second = list_rides(client, "past", first["nextCursor"]).get_json()

    assert len(first["items"]) == ride_rules.PAST_PAGE_SIZE
    assert second["nextCursor"] is None
    seen = [ride["id"] for ride in first["items"] + second["items"]]
    assert seen == list(reversed(created))


def test_a_ride_booked_between_two_pages_does_not_shift_them(client, clock):
    login(client)
    for _ in range(ride_rules.PAST_PAGE_SIZE + 1):
        clock.move(minutes=1)
        finished_ride(client)
    first = list_rides(client, "past").get_json()

    clock.move(minutes=1)
    finished_ride(client)  # newer than all: belongs to the first page, not the second
    second = list_rides(client, "past", first["nextCursor"]).get_json()

    assert len(second["items"]) == 1
    assert second["items"][0]["id"] not in [ride["id"] for ride in first["items"]]


def test_a_rider_only_sees_their_own_rides(client):
    login(client)
    booked_ride(client)

    login(client, phone=OTHER_RIDER_PHONE)

    assert list_rides(client, "upcoming").get_json()["items"] == []


def test_a_driver_sees_the_rides_they_took(client):
    login(client)
    taken = paid_ride(client)
    move_to(taken, ride_rules.ACCEPTED)
    paid_ride(client)  # waiting for a driver: not theirs

    login(client, phone=DRIVER_PHONE)

    assert ids(list_rides(client, "upcoming")) == [taken]


def test_the_call_centre_has_no_list_of_its_own(client):
    login(client, phone=OPERATOR_PHONE)

    assert list_rides(client, "upcoming").status_code == 403


@pytest.mark.parametrize(
    "query",
    [{}, {"when": "soon"}, {"when": "past", "cursor": "not-a-cursor"}, {"when": "upcoming", "cursor": "MjAyNnwx"}],
)
def test_a_wrong_list_query_is_refused(client, query):
    login(client)

    assert client.get("/rides", query_string=query).status_code == 400


# --- Cancellation ------------------------------------------------------------

def test_cancelling_a_paid_ride_refunds_it_in_full(client):
    login(client)
    ride_id = paid_ride(client)

    response = cancel(client, ride_id)

    assert response.status_code == 200
    ride = response.get_json()
    assert (ride["status"], ride["paymentStatus"]) == ("cancelled", "refunded")
    assert ride["cancelledAt"] is not None
    assert ids(list_rides(client, "past")) == [ride_id]


def test_a_ride_not_paid_yet_is_cancelled_without_refund(client):
    login(client)

    ride = cancel(client, booked_ride(client)).get_json()

    assert (ride["status"], ride["paymentStatus"]) == ("cancelled", "pending")


def test_a_ride_taken_by_a_driver_can_still_be_cancelled(client):
    login(client)
    ride_id = paid_ride(client)
    move_to(ride_id, ride_rules.ACCEPTED)

    assert cancel(client, ride_id).get_json()["status"] == "cancelled"


def test_cancelling_twice_is_not_an_error(client):
    login(client)
    ride_id = paid_ride(client)
    cancel(client, ride_id)

    response = cancel(client, ride_id)

    assert (response.status_code, response.get_json()["status"]) == (200, "cancelled")


@pytest.mark.parametrize("status", [ride_rules.IN_PROGRESS, ride_rules.COMPLETED])
def test_a_ride_already_started_cannot_be_cancelled(client, status):
    login(client)
    ride_id = paid_ride(client)
    move_to(ride_id, status)

    response = cancel(client, ride_id)

    assert response.status_code == 409
    assert "ne peut plus être annulé" in response.get_json()["detail"]


def test_a_rider_cannot_cancel_the_ride_of_another(client):
    login(client)
    ride_id = paid_ride(client)

    login(client, phone=OTHER_RIDER_PHONE)

    assert cancel(client, ride_id).status_code == 404


@pytest.mark.parametrize("phone", [OPERATOR_PHONE, ADMIN_PHONE])
def test_the_call_centre_and_the_administrators_may_cancel_for_a_rider(client, phone):
    login(client)
    ride_id = paid_ride(client)

    login(client, phone=phone)

    assert cancel(client, ride_id).get_json()["status"] == "cancelled"


def test_a_driver_cannot_cancel_a_ride(client):
    login(client)
    ride_id = paid_ride(client)
    move_to(ride_id, ride_rules.ACCEPTED)

    login(client, phone=DRIVER_PHONE)

    assert cancel(client, ride_id).status_code == 403


# --- Rating ------------------------------------------------------------------

def test_a_finished_ride_is_rated_once(client):
    login(client)
    ride_id = finished_ride(client)

    response = rate(client, ride_id, score=4, comment="  Très bien.  ")

    assert response.status_code == 201
    assert response.get_json()["rating"]["score"] == 4
    assert response.get_json()["rating"]["comment"] == "Très bien."
    assert client.get(f"/rides/{ride_id}").get_json()["rating"]["score"] == 4
    assert rate(client, ride_id).status_code == 409


def test_a_blank_comment_is_no_comment(client):
    login(client)

    assert rate(client, finished_ride(client), comment="   ").get_json()["rating"]["comment"] is None


@pytest.mark.parametrize("body", [{"score": 0}, {"score": 6}, {"score": 5, "comment": "x" * 501}, {}])
def test_a_wrong_rating_is_refused(client, body):
    login(client)

    response = client.post(f"/rides/{finished_ride(client)}/rating", json=body, headers=csrf_headers(client))

    assert response.status_code == 400


def test_a_ride_not_finished_cannot_be_rated(client):
    login(client)

    assert rate(client, paid_ride(client)).status_code == 409


def test_only_the_rider_of_the_ride_rates_it(client):
    login(client)
    ride_id = finished_ride(client)

    login(client, phone=OTHER_RIDER_PHONE)
    assert rate(client, ride_id).status_code == 404

    login(client, phone=DRIVER_PHONE)
    assert rate(client, ride_id).status_code == 403


# --- Development rides -------------------------------------------------------

def test_the_development_rides_let_alice_try_the_lists_and_the_rating(client):
    ride_repository.reset()
    login(client)

    past = list_rides(client, "past").get_json()["items"]

    assert [ride["status"] for ride in past] == ["completed", "completed", "cancelled", "completed"]
    assert [ride["rating"] is not None for ride in past] == [False, False, False, True]
    assert rate(client, past[0]["id"]).status_code == 201
