"""Real-time status of a ride and of the drivers' offers (contract, part 5).

The events are signals: `ride:updated` {rideId, status} to the people
following the ride, `offers:changed` to the drivers looking at the offers.
Each page then reads the ride again over HTTP.

One HTTP test client, logged in as several people in turn: a real-time
connection keeps the identity of the cookies it was opened with.
"""

import pytest

from app.extensions import socketio
from app.services import expiry_service
from app.utils import database
from tests.test_admin import as_admin, update
from tests.test_auth import RIDER_PHONE, login
from tests.test_drivers import DEMO_WAITING_RIDE, SECOND_DRIVER_PHONE, act, go_online, waiting_ride
from tests.test_ride_follow_up import cancel
from tests.test_rides import OTHER_RIDER_PHONE, book, booking

BRUNO_ID = 2  # OTHER_RIDER_PHONE, sql/demo-data.sql


def connect(app, client):
    """A real-time connection opened with the cookies of `client`'s current session."""
    return socketio.test_client(app, flask_test_client=client)


def follow(connection, ride_id) -> bool:
    return connection.emit("ride:follow", {"rideId": ride_id}, callback=True)["accepted"]


def follow_offers(connection) -> bool:
    return connection.emit("offers:follow", callback=True)["accepted"]


def events(connection) -> list[tuple[str, object]]:
    """The events received since the last call, as (name, content)."""
    received = connection.get_received()
    return [(event["name"], event["args"][0] if event["args"] else None) for event in received]


def ride_updates(connection) -> list[dict]:
    return [content for name, content in events(connection) if name == "ride:updated"]


def rider_following(app, client, ride_id, phone=RIDER_PHONE):
    login(client, phone=phone)
    connection = connect(app, client)
    assert follow(connection, ride_id)
    return connection


def driver_following_offers(app, client):
    go_online(client)
    connection = connect(app, client)
    assert follow_offers(connection)
    return connection


# --- Who may connect and follow ----------------------------------------------

def test_without_a_session_the_connection_is_refused(app, client):
    assert not connect(app, client).is_connected()


def test_a_logged_in_person_connects(app, client):
    login(client)
    assert connect(app, client).is_connected()


def test_a_rider_follows_their_ride_but_not_the_ride_of_another(app, client):
    ride_id = waiting_ride(client)

    rider_following(app, client, ride_id)
    login(client, phone=OTHER_RIDER_PHONE)
    assert not follow(connect(app, client), ride_id)


def test_an_unknown_ride_or_a_malformed_message_is_refused(app, client):
    login(client)
    connection = connect(app, client)

    assert not follow(connection, 999999)
    assert not connection.emit("ride:follow", {"rideId": "1; DROP"}, callback=True)["accepted"]
    assert not connection.emit("ride:follow", {"rideId": 1, "extra": True}, callback=True)["accepted"]


def test_only_a_driver_follows_the_offers(app, client):
    login(client, phone=RIDER_PHONE)
    assert not follow_offers(connect(app, client))

    go_online(client)
    assert follow_offers(connect(app, client))


def test_a_suspended_account_can_no_longer_follow_a_ride(app, client):
    """The connection outlives the token: the account is read again at every subscription."""
    login(client, phone=OTHER_RIDER_PHONE)
    connection = connect(app, client)

    as_admin(client)
    assert update(client, BRUNO_ID, status="suspended").status_code == 200

    assert not follow(connection, DEMO_WAITING_RIDE)


# --- What is announced -------------------------------------------------------

def test_the_rider_hears_of_each_step_of_their_ride(app, client):
    ride_id = waiting_ride(client)
    rider = rider_following(app, client, ride_id)
    go_online(client)

    act(client, ride_id, "accept")
    act(client, ride_id, "start")
    act(client, ride_id, "complete")

    assert ride_updates(rider) == [
        {"rideId": ride_id, "status": "accepted"},
        {"rideId": ride_id, "status": "in_progress"},
        {"rideId": ride_id, "status": "completed"},
    ]


def test_the_driver_hears_that_the_rider_cancelled(app, client):
    ride_id = waiting_ride(client)
    go_online(client)
    act(client, ride_id, "accept")
    driver = connect(app, client)
    assert follow(driver, ride_id)

    login(client, phone=RIDER_PHONE)
    assert cancel(client, ride_id).status_code == 200

    assert ride_updates(driver) == [{"rideId": ride_id, "status": "cancelled"}]


def test_the_drivers_hear_when_a_ride_enters_or_leaves_the_offers(app, client):
    driver = driver_following_offers(app, client)

    ride_id = waiting_ride(client)  # paid: it now waits for a driver
    assert ("offers:changed", None) in events(driver)

    go_online(client)
    act(client, ride_id, "accept")
    assert ("offers:changed", None) in events(driver)

    act(client, ride_id, "start")
    assert ("offers:changed", None) not in events(driver)


def test_an_unpaid_booking_changes_no_offer(app, client):
    driver = driver_following_offers(app, client)

    login(client)
    assert book(client, booking()).status_code == 201
    assert ("offers:changed", None) not in events(driver)


def test_the_rider_hears_that_no_driver_was_found(app, client, clock):
    ride_id = waiting_ride(client)
    rider = rider_following(app, client, ride_id)
    driver = driver_following_offers(app, client)
    events(driver)

    clock.move(minutes=16)
    expiry_service.expire_due_rides()

    assert {"rideId": ride_id, "status": "expired"} in ride_updates(rider)
    assert ("offers:changed", None) in events(driver)


def test_a_failed_write_announces_nothing(app, client):
    """A second acceptance loses the race: nothing changed, so nothing is told."""
    ride_id = waiting_ride(client)
    rider = rider_following(app, client, ride_id)
    go_online(client)
    act(client, ride_id, "accept")
    ride_updates(rider)

    go_online(client, phone=SECOND_DRIVER_PHONE)
    assert act(client, ride_id, "accept").status_code == 409

    assert ride_updates(rider) == []


def test_leaving_the_page_stops_the_events(app, client):
    ride_id = waiting_ride(client)
    rider = rider_following(app, client, ride_id)
    rider.emit("ride:unfollow", {"rideId": ride_id}, callback=True)

    go_online(client)
    act(client, ride_id, "accept")

    assert ride_updates(rider) == []


# --- Emission after the commit only -----------------------------------------

def test_an_action_after_commit_waits_for_the_commit():
    done = []
    with database.session() as session:
        database.after_commit(session, lambda: done.append("told"))
        assert done == []
    assert done == ["told"]


def test_an_action_after_commit_never_runs_after_a_rollback():
    done = []
    with pytest.raises(RuntimeError):
        with database.session() as session:
            database.after_commit(session, lambda: done.append("told"))
            raise RuntimeError("the write failed")
    assert done == []


def test_a_failed_action_after_commit_does_not_undo_the_write():
    with database.session() as session:
        database.after_commit(session, lambda: 1 / 0)
    # No exception: the write was saved, only the announcement failed (logged).
