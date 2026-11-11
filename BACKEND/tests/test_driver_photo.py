"""The driver's photo on the rider's trip page: to recognise them at the
pick-up, only while the ride is under way (like their phone number)."""

from tests.test_admin import TINY_JPEG, put_photo
from tests.test_auth import ADMIN_PHONE, RIDER_PHONE, login
from tests.test_drivers import act, go_online, send_position, waiting_ride
from tests.test_rides import OPERATOR_PHONE, OTHER_RIDER_PHONE

DRIVER_ID = 3  # Chloé, development account


def photo(client, ride_id):
    return client.get(f"/rides/{ride_id}/driver-photo")


def driver_of(client, ride_id):
    return client.get(f"/rides/{ride_id}").get_json()["driver"]


def accepted_ride(client, with_photo=True) -> int:
    """A ride of the rider (Alice), accepted by Chloé."""
    if with_photo:
        login(client, ADMIN_PHONE)
        put_photo(client, DRIVER_ID)
    ride_id = waiting_ride(client)
    go_online(client)
    send_position(client)
    act(client, ride_id, "accept")
    return ride_id


def test_the_rider_sees_the_driver_photo_while_the_ride_is_under_way(client):
    ride_id = accepted_ride(client)
    login(client, RIDER_PHONE)

    assert driver_of(client, ride_id)["photoUpdatedAt"] is not None
    response = photo(client, ride_id)
    assert (response.status_code, response.mimetype, response.data) == (200, "image/jpeg", TINY_JPEG)
    assert response.headers["Cache-Control"] == "private, max-age=86400"


def test_the_photo_is_gone_once_the_ride_is_over(client):
    ride_id = accepted_ride(client)
    act(client, ride_id, "start")
    act(client, ride_id, "complete")
    login(client, RIDER_PHONE)

    assert driver_of(client, ride_id)["photoUpdatedAt"] is None
    assert photo(client, ride_id).status_code == 404


def test_no_photo_before_a_driver_accepts(client):
    ride_id = waiting_ride(client)

    assert photo(client, ride_id).status_code == 404


def test_another_rider_never_sees_the_photo(client):
    """Same answer as a ride that does not exist: nothing to learn from it."""
    ride_id = accepted_ride(client)
    login(client, OTHER_RIDER_PHONE)

    assert photo(client, ride_id).status_code == 404


def test_the_call_centre_sees_the_photo(client):
    ride_id = accepted_ride(client)
    login(client, OPERATOR_PHONE)

    assert photo(client, ride_id).status_code == 200


def test_a_driver_without_photo_gives_nothing_to_show(client):
    ride_id = accepted_ride(client, with_photo=False)
    login(client, RIDER_PHONE)

    assert driver_of(client, ride_id)["photoUpdatedAt"] is None
    assert photo(client, ride_id).status_code == 404


def test_a_visitor_is_refused(client):
    ride_id = accepted_ride(client)
    visitor = client.application.test_client()

    assert photo(visitor, ride_id).status_code == 401
