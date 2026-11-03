"""
Forgotten password by SMS code (cahier des charges, §6 and §18): a person
without e-mail gets their account back with their phone. The code is typed in
POST /auth/activate, with the new password.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.repository.user_repository import DEV_PASSWORD
from app.services import auth_service
from app.services.auth_service import (
    DEMO_PASSWORD_RESET_CODE,
    MAX_CODES_PER_ADDRESS,
    MAX_CODES_PER_PHONE,
    PASSWORD_RESET_CODE_VALIDITY,
)
from tests.test_auth import (
    ADMIN_PHONE,
    DRIVER_PHONE,
    NEW_PASSWORD,
    RIDER_PHONE,
    SUSPENDED_PHONE,
    TO_ACTIVATE_PHONE,
    activate,
    login,
)
from tests.test_registration import sms_kinds

OPERATOR_PHONE = "0694 00 00 05"
UNKNOWN_PHONE = "0694 99 99 99"


def ask_code(client, phone=RIDER_PHONE):
    return client.post("/auth/password-reset", json={"phone": phone})


def test_a_rider_sets_a_new_password_with_the_sms_code(client):
    assert ask_code(client).status_code == 202

    response = activate(client, code=DEMO_PASSWORD_RESET_CODE, phone=RIDER_PHONE)

    assert response.status_code == 200
    assert client.get("/auth/me").get_json()["phone"] == "+594694000001"
    assert login(client, password=NEW_PASSWORD).status_code == 200
    assert login(client, password=DEV_PASSWORD).status_code == 401


def test_the_sessions_opened_with_the_old_password_end(client, app):
    login(client)
    ask_code(app.test_client())

    activate(app.test_client(), code=DEMO_PASSWORD_RESET_CODE, phone=RIDER_PHONE)

    assert client.get("/auth/me").status_code == 401


def test_asking_a_code_keeps_the_current_password(client):
    # Anyone can type someone else's number: that alone must not lock them out.
    ask_code(client)

    assert login(client).status_code == 200


@pytest.mark.parametrize("phone", [DRIVER_PHONE, OPERATOR_PHONE])
def test_staff_other_than_administrators_can_reset(client, phone):
    ask_code(client, phone=phone)

    assert activate(client, code=DEMO_PASSWORD_RESET_CODE, phone=phone).status_code == 200


def test_an_administrator_gets_no_code(client, caplog):
    response = ask_code(client, phone=ADMIN_PHONE)

    assert response.status_code == 202
    assert sms_kinds(caplog) == []
    assert activate(client, code=DEMO_PASSWORD_RESET_CODE, phone=ADMIN_PHONE).status_code == 422


def test_a_suspended_account_gets_no_code(client, caplog):
    assert ask_code(client, phone=SUSPENDED_PHONE).status_code == 202
    assert sms_kinds(caplog) == []


def test_the_answer_does_not_tell_who_has_an_account(client, caplog):
    answers = [ask_code(client, phone=phone) for phone in (RIDER_PHONE, UNKNOWN_PHONE, ADMIN_PHONE)]

    assert {answer.status_code for answer in answers} == {202}
    assert {tuple(answer.get_json()) for answer in answers} == {("expiresAt",)}
    assert sms_kinds(caplog) == ["password_reset_code"]


def test_the_code_expires_after_15_minutes(client, monkeypatch):
    ask_code(client)
    later = datetime.now(timezone.utc) + PASSWORD_RESET_CODE_VALIDITY + timedelta(seconds=1)
    monkeypatch.setattr(auth_service, "datetime", type("Clock", (), {"now": staticmethod(lambda tz=None: later)}))

    assert activate(client, code=DEMO_PASSWORD_RESET_CODE, phone=RIDER_PHONE).status_code == 422


def test_the_code_is_used_once(client):
    ask_code(client)
    activate(client, code=DEMO_PASSWORD_RESET_CODE, phone=RIDER_PHONE)

    assert activate(client, code=DEMO_PASSWORD_RESET_CODE, phone=RIDER_PHONE).status_code == 422


def test_a_new_code_replaces_the_one_handed_over_by_the_team(client):
    # The development account to activate has the code 12345678; outside the
    # demo, the SMS code is random and takes its place.
    auth_service.configure(demo_codes=False)
    ask_code(client, phone=TO_ACTIVATE_PHONE)

    assert activate(client).status_code == 422


def test_neither_the_number_nor_the_code_reaches_the_logs(client, caplog):
    auth_service.configure(demo_codes=False)
    ask_code(client)

    assert "694" not in caplog.text
    assert DEMO_PASSWORD_RESET_CODE not in caplog.text


def test_codes_are_limited_per_number(client):
    for _ in range(MAX_CODES_PER_PHONE):
        assert ask_code(client).status_code == 202

    assert ask_code(client).status_code == 429


def test_codes_are_limited_per_network_address(client):
    for number in range(MAX_CODES_PER_ADDRESS):
        assert ask_code(client, phone=f"0694 70 00 {number:02d}").status_code == 202

    assert ask_code(client, phone="0694 71 00 00").status_code == 429


def test_a_wrong_number_is_refused_on_its_field(client):
    response = ask_code(client, phone="12")

    assert response.status_code == 400
    assert response.get_json()["detail"]["fields"][0]["field"] == "phone"
