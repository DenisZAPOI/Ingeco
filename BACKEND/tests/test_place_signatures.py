"""
Stops signed by the API (audit F9), offers read by drivers (F10), and the SMS
to the holder of an account given a new code (F19).
"""

from app.services.place_service import PLACE_NOT_PROPOSED
from tests.test_auth import ADMIN_PHONE, DRIVER_PHONE, RIDER_PHONE, csrf_headers, login
from tests.test_drivers import SECOND_DRIVER_PHONE, go_online, second_driver, waiting_ride  # noqa: F401
from tests.test_rides import MATOURY_TOWN_HALL, OTHER_RIDER_PHONE, signed

AIRPORT_NEXT_DOOR = {"address": "Aéroport Félix Éboué, Matoury", "lat": 4.9380, "lng": -52.3262, "communeId": 3}


def proposed_place(client, search="mairie", commune_id=1) -> dict:
    place = client.get("/places", query_string={"search": search, "communeId": commune_id}).get_json()["items"][0]
    return {"address": place["label"], "lat": place["lat"], "lng": place["lng"], "communeId": place["communeId"],
            "token": place["token"]}


def estimate(client, pickup, dropoff):
    return client.post("/rides/estimate", json={"pickup": pickup, "dropoff": dropoff}, headers=csrf_headers(client))


# --- F9 ---------------------------------------------------------------------------

def test_a_place_proposed_by_the_api_is_accepted_as_is(client):
    login(client)
    pickup, dropoff = proposed_place(client), proposed_place(client, commune_id=3)

    assert estimate(client, pickup, dropoff).status_code == 200


def test_a_label_typed_apart_from_its_position_is_refused(client):
    login(client)
    pickup = proposed_place(client)
    real = proposed_place(client, commune_id=3)

    response = estimate(client, pickup, real | {"address": "Aéroport Félix Éboué, Matoury"})

    assert response.status_code == 422
    assert response.get_json()["detail"] == PLACE_NOT_PROPOSED


def test_a_moved_position_is_refused(client):
    login(client)
    pickup, dropoff = proposed_place(client), proposed_place(client, commune_id=3)

    assert estimate(client, pickup, dropoff | {"lat": AIRPORT_NEXT_DOOR["lat"]}).status_code == 422


def test_another_commune_is_refused(client):
    login(client)
    pickup, dropoff = proposed_place(client), proposed_place(client, commune_id=3)

    assert estimate(client, pickup, dropoff | {"communeId": 1}).status_code == 422


def test_a_stop_without_token_is_refused_on_its_field(client):
    login(client)

    response = estimate(client, signed(MATOURY_TOWN_HALL), AIRPORT_NEXT_DOOR)

    assert response.status_code == 400
    assert response.get_json()["detail"]["fields"][0]["field"] == "dropoff.token"


def test_the_stops_of_a_ride_can_be_booked_again(client):
    ride = waiting_ride(client)
    stops = client.get(f"/rides/{ride}").get_json()
    client.post(f"/rides/{ride}/cancel", headers=csrf_headers(client))

    assert estimate(client, stops["pickup"], stops["dropoff"]).status_code == 200


# --- F10 --------------------------------------------------------------------------

def test_an_offline_driver_cannot_read_a_waiting_ride(client):
    ride = waiting_ride(client)

    login(client, phone=DRIVER_PHONE)

    assert client.get(f"/rides/{ride}").status_code == 404


def test_an_online_driver_reads_a_waiting_ride(client):
    ride = waiting_ride(client)

    go_online(client)

    assert client.get(f"/rides/{ride}").status_code == 200


def test_a_ride_needing_an_accessible_vehicle_is_hidden_from_other_drivers(client, second_driver):  # noqa: F811
    ride = waiting_ride(client, phone=OTHER_RIDER_PHONE)  # Bruno needs an accessible vehicle

    go_online(client, phone=SECOND_DRIVER_PHONE)

    assert client.get(f"/rides/{ride}").status_code == 404


def test_a_rider_still_cannot_read_the_ride_of_another(client):
    ride = waiting_ride(client)

    login(client, phone=OTHER_RIDER_PHONE)

    assert client.get(f"/rides/{ride}").status_code == 404


# --- F19 --------------------------------------------------------------------------

def sms_kinds(caplog):
    return [record.context["kind"] for record in caplog.records if record.getMessage() == "SMS simulated"]


def test_the_holder_of_an_active_account_is_warned_of_a_new_code(client, caplog):
    login(client, phone=ADMIN_PHONE)

    client.post("/admin/users/1/activation-code", headers=csrf_headers(client))

    assert sms_kinds(caplog) == ["new_activation_code"]


def test_an_account_never_activated_gets_no_warning(client, caplog):
    login(client, phone=ADMIN_PHONE)

    client.post("/admin/users/7/activation-code", headers=csrf_headers(client))  # Gaëlle, no password yet

    assert sms_kinds(caplog) == []


def test_a_rider_cannot_issue_a_code(client):
    login(client, phone=RIDER_PHONE)

    assert client.post("/admin/users/1/activation-code", headers=csrf_headers(client)).status_code == 403
