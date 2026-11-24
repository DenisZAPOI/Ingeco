"""The person's rights on their data (audit RGPD R3, R4, R10): deletion request
and anonymisation, « Mes données », callbacks for the staff, retention.

Accounts of sql/demo-data.sql: Alice (1, rider), Chloé (3, driver), the
operator (5) and the administrator (6).
"""

import pytest
from sqlalchemy import select

from app.models import AnswerRow, QuestionnaireRow, RideRow, UserRow
from app.services import retention_service
from app.utils import database
from tests.test_auth import ADMIN_PHONE, DRIVER_PHONE, RIDER_PHONE, csrf_headers, login
from tests.test_drivers import act, go_online, waiting_ride
from tests.test_orientation import JORDAN
from tests.test_rides import CAYENNE_TOWN_HALL, OPERATOR_PHONE, book

ALICE_ID = 1
CHLOE_ID = 3
CALLBACK_PHONE = "0694 11 22 33"


def ask_deletion(client, phone=RIDER_PHONE):
    login(client, phone=phone)
    return client.post("/users/me/deletion-request", headers=csrf_headers(client))


def anonymise(client, user_id=ALICE_ID):
    login(client, phone=ADMIN_PHONE)
    return client.post(f"/admin/users/{user_id}/anonymise", headers=csrf_headers(client))


def row_of(user_id: int) -> UserRow:
    with database.session() as session:
        row = session.get(UserRow, user_id)
        session.expunge(row)
        return row


# --- The deletion request ----------------------------------------------------------

def test_a_rider_asks_to_delete_their_account_once(client):
    first = ask_deletion(client).get_json()
    again = client.post("/users/me/deletion-request", headers=csrf_headers(client)).get_json()

    assert again["requestedAt"] == first["requestedAt"]
    assert client.get("/users/me/deletion-request").get_json() == first


def test_a_request_can_be_withdrawn_before_it_is_handled(client):
    ask_deletion(client)

    assert client.delete("/users/me/deletion-request", headers=csrf_headers(client)).status_code == 204
    assert client.get("/users/me/deletion-request").status_code == 404
    # Twice: a double tap is not an error.
    assert client.delete("/users/me/deletion-request", headers=csrf_headers(client)).status_code == 204


def test_a_driver_may_ask_too(client):
    assert ask_deletion(client, phone=DRIVER_PHONE).status_code == 200


def test_a_staff_account_is_deleted_by_an_administrator_only(client):
    assert ask_deletion(client, phone=OPERATOR_PHONE).status_code == 403


def test_the_administrator_sees_the_open_requests(client):
    ask_deletion(client)
    login(client, phone=ADMIN_PHONE)

    items = client.get("/admin/deletion-requests").get_json()["items"]

    assert [item["userId"] for item in items] == [ALICE_ID]
    assert items[0]["firstName"] == "Alice"


@pytest.mark.parametrize("phone", [RIDER_PHONE, DRIVER_PHONE, OPERATOR_PHONE])
def test_only_an_administrator_handles_the_requests(client, phone):
    login(client, phone=phone)

    assert client.get("/admin/deletion-requests").status_code == 403
    assert client.post(f"/admin/users/{ALICE_ID}/anonymise", headers=csrf_headers(client)).status_code == 403


# --- Anonymisation ---------------------------------------------------------------

def test_anonymising_keeps_nothing_that_names_the_person(client):
    ask_deletion(client)

    assert anonymise(client).status_code == 204

    row = row_of(ALICE_ID)
    assert row.status == "supprime"
    assert (row.first_name, row.last_name, row.email, row.password_hash) == ("", "", None, None)
    assert row.phone == "+000000000001"
    assert login(client, phone=RIDER_PHONE).status_code == 401
    # Out of the lists, and of the requests.
    login(client, phone=ADMIN_PHONE)
    assert client.get(f"/admin/users/{ALICE_ID}").status_code == 404
    assert client.get("/admin/deletion-requests").get_json()["items"] == []


def test_the_rides_stay_with_only_their_communes(client):
    ask_deletion(client)
    anonymise(client)

    with database.session() as session:
        rides = session.scalars(select(RideRow).where(RideRow.rider_id == ALICE_ID)).all()
        stops = {(ride.pickup_address, ride.pickup_landmark) for ride in rides}

    assert rides
    assert CAYENNE_TOWN_HALL["address"] not in {address for address, _ in stops}
    assert {landmark for _, landmark in stops} == {None}


def test_a_ride_no_driver_took_is_cancelled(client):
    login(client)
    ride_id = book(client).get_json()["id"]
    ask_deletion(client)

    anonymise(client)

    login(client, phone=ADMIN_PHONE)
    assert client.get(f"/rides/{ride_id}").get_json()["status"] == "cancelled"


def test_a_ride_a_driver_holds_waits_for_its_end(client):
    ride_id = waiting_ride(client)
    go_online(client)
    act(client, ride_id, "accept")
    ask_deletion(client)

    response = anonymise(client)

    assert response.status_code == 409
    assert row_of(ALICE_ID).status == "actif"


def test_an_account_without_a_request_is_not_anonymised(client):
    assert anonymise(client).status_code == 409


def test_a_driver_loses_photo_and_position(client):
    go_online(client)
    ask_deletion(client, phone=DRIVER_PHONE)

    assert anonymise(client, CHLOE_ID).status_code == 204

    login(client, phone=ADMIN_PHONE)
    assert client.get(f"/admin/users/{CHLOE_ID}/photo").status_code == 404


# --- « Mes données » -------------------------------------------------------------

def test_my_data_holds_the_account_the_rides_and_the_plan(client):
    login(client)
    client.post("/orientation/questionnaires", json=JORDAN, headers=csrf_headers(client))

    data = client.get("/users/me/data").get_json()

    assert data["account"]["firstName"] == "Alice"
    assert data["rides"]
    assert data["plan"]["answers"]["experienceText"] == JORDAN["experienceText"]
    assert data["deletionRequestedAt"] is None


def test_a_driver_sees_their_rides_as_in_the_app(client):
    login(client, phone=DRIVER_PHONE)

    rides = client.get("/users/me/data").get_json()["rides"]

    assert rides
    assert all(ride["purpose"] is None for ride in rides)


def test_my_data_needs_a_login(client):
    assert client.get("/users/me/data").status_code == 401


# --- Callbacks for the staff (R10) -------------------------------------------------

def test_the_operator_calls_back_then_marks_it_handled(client):
    client.post("/help-requests/callback", json={"phone": CALLBACK_PHONE})
    login(client, phone=OPERATOR_PHONE)

    items = client.get("/help-requests/callbacks").get_json()["items"]
    handled = client.post(f"/help-requests/{items[0]['id']}/handled", headers=csrf_headers(client))

    assert items[0]["phone"] == "+594694112233"
    assert items[0]["hasAccount"] is False
    assert handled.status_code == 204
    assert client.get("/help-requests/callbacks").get_json()["items"] == []
    # Twice: already handled.
    assert client.post(f"/help-requests/{items[0]['id']}/handled", headers=csrf_headers(client)).status_code == 404


@pytest.mark.parametrize("phone", [RIDER_PHONE, DRIVER_PHONE])
def test_only_the_staff_sees_the_callbacks(client, phone):
    login(client, phone=phone)

    assert client.get("/help-requests/callbacks").status_code == 403


# --- Retention (R4) -------------------------------------------------------------------

def test_a_handled_callback_is_deleted_three_months_later(client, clock):
    client.post("/help-requests/callback", json={"phone": CALLBACK_PHONE})
    login(client, phone=OPERATOR_PHONE)
    request_id = client.get("/help-requests/callbacks").get_json()["items"][0]["id"]
    client.post(f"/help-requests/{request_id}/handled", headers=csrf_headers(client))

    clock.move(days=89)
    assert retention_service.purge().help_requests_deleted == 0
    clock.move(days=2)
    assert retention_service.purge().help_requests_deleted == 1


def test_a_ride_keeps_its_exact_stops_for_a_year(client, clock):
    ride_id = waiting_ride(client)
    go_online(client)
    for action in ("accept", "start", "complete"):
        act(client, ride_id, action)

    clock.move(days=364)
    retention_service.purge()
    assert _pickup_of(ride_id) == CAYENNE_TOWN_HALL["address"]

    clock.move(days=2)
    retention_service.purge()
    assert _pickup_of(ride_id) == "Cayenne"
    # A second run changes nothing.
    assert retention_service.purge().rides_reduced == 0


def test_a_new_questionnaire_replaces_the_older_one(client):
    login(client)
    client.post("/orientation/questionnaires", json=JORDAN, headers=csrf_headers(client))
    client.post("/orientation/questionnaires", json=JORDAN, headers=csrf_headers(client))

    with database.session() as session:
        fillings = session.scalars(select(QuestionnaireRow).where(QuestionnaireRow.rider_id == ALICE_ID)).all()
        texts = session.scalars(
            select(AnswerRow.text)
            .join(QuestionnaireRow, QuestionnaireRow.id == AnswerRow.questionnaire_id)
            .where(QuestionnaireRow.rider_id == ALICE_ID, AnswerRow.text.is_not(None))
        ).all()

    assert len(fillings) == 1
    assert len(texts) == 1


def _pickup_of(ride_id: int) -> str:
    with database.session() as session:
        return session.scalar(select(RideRow.pickup_address).where(RideRow.id == ride_id))
