"""PATCH /users/me: the logged-in user changes their own profile."""

from app.repository.user_repository import DEV_PASSWORD
from tests.test_auth import DRIVER_PHONE, csrf_headers, login


def update(client, **body):
    return client.patch("/users/me", json=body, headers=csrf_headers(client))


def test_a_rider_changes_name_email_and_accessibility_need(client):
    login(client)

    response = update(client, firstName=" Alicia ", email="alicia@exemple.fr", needsAccessibleVehicle=True)

    assert response.status_code == 200
    user = response.get_json()
    assert (user["firstName"], user["lastName"]) == ("Alicia", "Démo")  # last name untouched
    assert (user["email"], user["needsAccessibleVehicle"]) == ("alicia@exemple.fr", True)


def test_sending_null_removes_the_email(client):
    login(client)
    update(client, email="alicia@exemple.fr")

    assert update(client, email=None).get_json()["email"] is None


def test_the_phone_number_cannot_be_changed_here(client):
    login(client)

    assert update(client, phone="0694 11 11 11").status_code == 400


def test_a_write_without_the_csrf_header_is_refused(client):
    login(client)

    assert client.patch("/users/me", json={"firstName": "Pirate"}).status_code == 401


def test_changing_the_password_requires_the_current_one(client):
    login(client)

    without_current = update(client, newPassword="Nouveau-2026!")
    wrong_current = update(client, currentPassword="Pas-le-bon-1", newPassword="Nouveau-2026!")
    right_current = update(client, currentPassword=DEV_PASSWORD, newPassword="Nouveau-2026!")

    assert without_current.status_code == 400
    assert wrong_current.status_code == 422
    assert right_current.status_code == 200
    assert login(client, password="Nouveau-2026!").status_code == 200


def test_an_email_used_by_another_account_is_refused(client):
    login(client, phone=DRIVER_PHONE)
    update(client, email="partagee@exemple.fr")
    login(client)

    assert update(client, email="partagee@exemple.fr").status_code == 409


def test_the_accessibility_need_only_concerns_riders(client):
    login(client, phone=DRIVER_PHONE)

    assert update(client, needsAccessibleVehicle=True).status_code == 422


def test_an_anonymous_caller_cannot_change_a_profile(client):
    assert client.patch("/users/me", json={"firstName": "Personne"}).status_code == 401
