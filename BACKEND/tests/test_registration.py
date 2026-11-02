"""
Registration proven by an SMS code (audit F4): nothing is created before the
code is typed, and the API never tells whether a number has an account.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.repository import user_repository
from app.services import auth_service
from app.services.auth_service import (
    DEMO_REGISTRATION_CODE,
    EMAIL_TAKEN_AT_REGISTRATION,
    MAX_CODES_PER_ADDRESS,
    MAX_CODES_PER_PHONE,
    MAX_FAILED_ATTEMPTS,
    REGISTRATION_CODE_VALIDITY,
    WRONG_REGISTRATION_CODE,
)
from tests.test_auth import RIDER_PHONE, TO_ACTIVATE_PHONE, login, new_rider, register

NEW_PHONE = "0694 99 99 99"
WRONG_CODE = "000000"


def ask_code(client, **changes):
    return client.post("/auth/register", json=new_rider(**changes))


def confirm(client, code=DEMO_REGISTRATION_CODE, phone=NEW_PHONE):
    return client.post("/auth/register/confirm", json={"phone": phone, "code": code})


def sms_kinds(caplog):
    return [record.context["kind"] for record in caplog.records if record.getMessage() == "SMS simulated"]


def test_asking_a_code_creates_no_account(client):
    response = ask_code(client)

    assert response.status_code == 202
    assert "expiresAt" in response.get_json()
    assert user_repository.find_by_phone(None, "+594694999999") is None
    assert login(client, phone=NEW_PHONE, password=new_rider()["password"]).status_code == 401


def test_the_right_code_creates_the_account_and_opens_the_session(client):
    ask_code(client)

    response = confirm(client)

    assert response.status_code == 201
    assert client.get("/auth/me").get_json()["phone"] == "+594694999999"


def test_a_code_is_used_once(client, app):
    ask_code(client)
    confirm(client)
    other_phone = app.test_client()

    assert confirm(other_phone).status_code == 422
    assert other_phone.get("/auth/me").status_code == 401


def test_a_wrong_code_creates_nothing(client):
    ask_code(client)

    response = confirm(client, code=WRONG_CODE)

    assert response.status_code == 422
    assert response.get_json()["detail"] == WRONG_REGISTRATION_CODE
    assert user_repository.find_by_phone(None, "+594694999999") is None


def test_an_expired_code_fails(client, monkeypatch):
    ask_code(client)
    later = datetime.now(timezone.utc) + REGISTRATION_CODE_VALIDITY + timedelta(seconds=1)
    monkeypatch.setattr(auth_service, "datetime", type("Clock", (), {"now": staticmethod(lambda tz=None: later)}))

    assert confirm(client).status_code == 422


def test_after_5_wrong_codes_a_new_one_must_be_asked(client):
    ask_code(client)
    for _ in range(MAX_FAILED_ATTEMPTS):
        confirm(client, code=WRONG_CODE)

    assert confirm(client).status_code == 422
    ask_code(client)
    assert confirm(client).status_code == 201


def test_a_new_code_replaces_the_registration_of_someone_else(client):
    # Someone types the number of another person: they never get the code, and
    # the real holder can still register.
    ask_code(client, firstName="Usurpateur")

    ask_code(client, firstName="Inès")

    assert confirm(client).get_json()["firstName"] == "Inès"


def test_a_number_with_an_account_gets_the_same_answer(client, caplog):
    taken = ask_code(client, phone=RIDER_PHONE)
    free = ask_code(client)

    assert taken.status_code == free.status_code == 202
    assert taken.get_json().keys() == free.get_json().keys()
    assert sms_kinds(caplog) == ["already_registered", "registration_code"]


def test_a_number_with_an_account_cannot_be_registered_again(client):
    ask_code(client, phone=TO_ACTIVATE_PHONE)

    assert confirm(client, phone=TO_ACTIVATE_PHONE).status_code == 422


def test_neither_the_number_nor_the_code_reaches_the_logs(client, caplog):
    auth_service.configure(demo_codes=False)
    ask_code(client)

    assert "694" not in caplog.text
    assert DEMO_REGISTRATION_CODE not in caplog.text


def test_outside_the_demo_the_code_is_random(client):
    auth_service.configure(demo_codes=False)
    ask_code(client)

    assert confirm(client).status_code == 422


def test_an_email_already_used_is_told_once_the_phone_is_proven(client):
    ask_code(client, email="alice@example.org")
    user_repository.insert_user(
        None, user_repository.User(role="rider", status="active", first_name="A", last_name="B",
                                   phone="+594694888888", email="alice@example.org")
    )

    response = confirm(client)

    assert response.status_code == 409
    assert response.get_json()["detail"] == EMAIL_TAKEN_AT_REGISTRATION


def test_codes_are_limited_per_number(client):
    for _ in range(MAX_CODES_PER_PHONE):
        assert ask_code(client).status_code == 202

    assert ask_code(client).status_code == 429


def test_codes_are_limited_per_network_address(client):
    for number in range(MAX_CODES_PER_ADDRESS):
        assert ask_code(client, phone=f"0694 70 00 {number:02d}").status_code == 202

    assert ask_code(client, phone="0694 71 00 00").status_code == 429


@pytest.mark.parametrize("code", ["12345", "1234567", "abcdef"])
def test_a_code_of_another_shape_is_refused_on_its_field(client, code):
    response = confirm(client, code=code)

    assert response.status_code == 400
    assert response.get_json()["detail"]["fields"][0]["field"] == "code"


def test_the_helper_still_registers(client):
    assert register(client).status_code == 201
