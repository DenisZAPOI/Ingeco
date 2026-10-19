"""
Authentication routes, through HTTP: registration, login, activation, session
renewal, logout, and the role check.

The development accounts of repository/user_repository.py are reset before
each test (see conftest.py).
"""

from app.repository.user_repository import DEV_ACTIVATION_CODE, DEV_PASSWORD
from app.services.auth_service import MAX_FAILED_ATTEMPTS

RIDER_PHONE = "0694 00 00 01"
DRIVER_PHONE = "0694 00 00 03"
ADMIN_PHONE = "0694 00 00 06"
TO_ACTIVATE_PHONE = "0694 00 00 07"
SUSPENDED_PHONE = "0694 00 00 08"
NEW_PASSWORD = "Nouveau-mot2passe"


def login(client, phone=RIDER_PHONE, password=DEV_PASSWORD):
    return client.post("/auth/login", json={"phone": phone, "password": password})


def csrf_headers(client, cookie="csrf_access_token"):
    """What the front-end does: copy the readable CSRF cookie into the header."""
    return {"X-CSRF-TOKEN": client.get_cookie(cookie).value}


def new_rider(**changes):
    body = {
        "firstName": "Inès",
        "lastName": "Exemple",
        "phone": "0694 99 99 99",
        "password": "Bonjour-2026",
        "email": None,
        "needsAccessibleVehicle": False,
    }
    return body | changes


# ---------------------------------------------------------------------------
#  Registration
# ---------------------------------------------------------------------------

def test_a_visitor_registers_as_a_rider_and_is_logged_in(client):
    response = client.post("/auth/register", json=new_rider())

    assert response.status_code == 201
    user = response.get_json()
    assert (user["role"], user["status"], user["phone"]) == ("rider", "active", "+594694999999")
    assert user["isPriority"] is False
    assert client.get("/auth/me").get_json()["id"] == user["id"]


def test_the_session_cookies_are_http_only(client):
    response = client.post("/auth/register", json=new_rider())

    cookies = response.headers.getlist("Set-Cookie")
    access = next(cookie for cookie in cookies if cookie.startswith("access_token_cookie="))
    csrf = next(cookie for cookie in cookies if cookie.startswith("csrf_access_token="))
    assert "HttpOnly" in access
    assert "HttpOnly" not in csrf  # the front-end must be able to read this one


def test_registration_cannot_choose_another_role(client):
    response = client.post("/auth/register", json=new_rider(role="admin"))

    assert response.status_code == 400


def test_a_number_already_registered_is_refused(client):
    response = client.post("/auth/register", json=new_rider(phone=TO_ACTIVATE_PHONE))

    assert response.status_code == 409
    assert "J'ai reçu un code" in response.get_json()["detail"]


def test_a_weak_password_is_refused_with_a_french_message_on_the_field(client):
    response = client.post("/auth/register", json=new_rider(password="motdepasse", firstName=None))

    assert response.status_code == 400
    messages = {field["field"]: field["message"] for field in response.get_json()["detail"]["fields"]}
    assert messages["password"].startswith("Le mot de passe doit contenir")
    assert messages["firstName"] == "Valeur invalide."


# ---------------------------------------------------------------------------
#  Login
# ---------------------------------------------------------------------------

def test_login_with_the_number_as_typed_by_the_user(client):
    response = login(client, phone="06.94.00.00.01")

    assert response.status_code == 200
    assert response.get_json()["firstName"] == "Alice"


def test_a_wrong_password_and_an_unknown_number_get_the_same_answer(client):
    wrong_password = login(client, password="Pas-le-bon-1")
    unknown_number = login(client, phone="0694 55 55 55")

    assert wrong_password.status_code == unknown_number.status_code == 401
    assert wrong_password.get_json() == unknown_number.get_json()


def test_an_account_not_activated_cannot_log_in(client):
    assert login(client, phone=TO_ACTIVATE_PHONE, password="").status_code == 400
    assert login(client, phone=TO_ACTIVATE_PHONE, password=DEV_PASSWORD).status_code == 401


def test_a_suspended_account_cannot_log_in(client):
    assert login(client, phone=SUSPENDED_PHONE).status_code == 403


def test_login_is_blocked_after_too_many_failures_even_with_the_right_password(client):
    for _ in range(MAX_FAILED_ATTEMPTS):
        login(client, password="Pas-le-bon-1")

    response = login(client)

    assert response.status_code == 429
    assert login(client, phone=DRIVER_PHONE).status_code == 200  # other numbers are not affected


# ---------------------------------------------------------------------------
#  Activation
# ---------------------------------------------------------------------------

def activate(client, code=DEV_ACTIVATION_CODE, phone=TO_ACTIVATE_PHONE):
    return client.post("/auth/activate", json={"phone": phone, "code": code, "password": NEW_PASSWORD})


def test_an_account_created_by_the_call_centre_is_activated_with_its_code(client):
    response = activate(client, code="1234 5678")

    assert response.status_code == 200
    assert client.get("/auth/me").status_code == 200
    assert login(client, phone=TO_ACTIVATE_PHONE, password=NEW_PASSWORD).status_code == 200


def test_an_activation_code_is_single_use(client):
    activate(client)

    assert activate(client).status_code == 422


def test_a_wrong_code_and_an_unknown_number_get_the_same_answer(client):
    wrong_code = activate(client, code="87654321")
    unknown_number = activate(client, phone="0694 55 55 55")

    assert wrong_code.status_code == unknown_number.status_code == 422
    assert wrong_code.get_json() == unknown_number.get_json()


def test_activation_is_blocked_after_too_many_failures(client):
    for _ in range(MAX_FAILED_ATTEMPTS):
        activate(client, code="87654321")

    assert activate(client).status_code == 429


# ---------------------------------------------------------------------------
#  Session: renewal, logout, role check
# ---------------------------------------------------------------------------

def test_without_a_session_the_account_is_not_readable(client):
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized", "detail": "Vous devez vous connecter."}


def test_the_session_is_renewed_with_the_refresh_cookie(client):
    login(client)

    response = client.post("/auth/refresh", headers=csrf_headers(client, "csrf_refresh_token"))

    assert response.status_code == 200
    assert response.get_json()["firstName"] == "Alice"


def test_renewal_without_the_csrf_header_is_refused(client):
    login(client)

    assert client.post("/auth/refresh").status_code == 401


def test_a_suspended_account_loses_its_session_at_renewal(client):
    from app.repository import user_repository

    login(client)
    user = user_repository.find_by_phone(None, "+594694000001")
    user.status = "suspended"
    user_repository.update_user(None, user)

    response = client.post("/auth/refresh", headers=csrf_headers(client, "csrf_refresh_token"))

    assert response.status_code == 401
    assert client.get_cookie("access_token_cookie") is None


def test_logout_erases_the_session(client):
    login(client)

    assert client.post("/auth/logout").status_code == 204
    assert client.get("/auth/me").status_code == 401


def test_a_role_not_allowed_is_refused(client):
    login(client)  # a rider

    assert client.get("/_tests/admin-only").status_code == 403


def test_the_allowed_role_gets_through(client):
    login(client, phone=ADMIN_PHONE)

    assert client.get("/_tests/admin-only").status_code == 204
