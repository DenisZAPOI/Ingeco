"""
Ending sessions (audit F2, F3, F8): the account is reread at every request,
and a new password or a suspension ends the sessions opened before.
"""

from flask_jwt_extended import create_access_token

from app.repository import user_repository
from app.repository.user_repository import User
from app.services.admin_service import NOT_YOURSELF
from app.utils import database
from app.utils.passwords import hash_secret
from tests.test_auth import ADMIN_PHONE, DEV_PASSWORD, NEW_PASSWORD, RIDER_PHONE, csrf_headers, login

RIDER_ID = 1
ADMIN_ID = 6
OTHER_ADMIN_PHONE = "0694 11 11 11"


def logged_in(app, phone=RIDER_PHONE, password=DEV_PASSWORD):
    client = app.test_client()
    assert login(client, phone=phone, password=password).status_code == 200
    return client


def refresh(client):
    return client.post("/auth/refresh", headers=csrf_headers(client, "csrf_refresh_token"))


def change_password(client):
    return client.patch(
        "/users/me", json={"currentPassword": DEV_PASSWORD, "newPassword": NEW_PASSWORD}, headers=csrf_headers(client)
    )


def set_status(admin, user_id, status):
    return admin.patch(f"/admin/users/{user_id}", json={"status": status}, headers=csrf_headers(admin))


def other_admin(app):
    with database.session() as session:
        user_repository.insert_user(
            session,
            User(role="admin", status="active", first_name="Second", last_name="Démo", phone="+594694111111",
                 password_hash=hash_secret(DEV_PASSWORD)),
        )
    return logged_in(app, OTHER_ADMIN_PHONE)


# --- New password ------------------------------------------------------------

def test_a_new_password_ends_the_sessions_of_the_other_phones(app):
    lost_phone, own_phone = logged_in(app), logged_in(app)

    assert change_password(own_phone).status_code == 200

    assert lost_phone.get("/auth/me").status_code == 401
    assert refresh(lost_phone).status_code == 401


def test_the_phone_that_changed_the_password_stays_logged_in(app):
    own_phone = logged_in(app)

    change_password(own_phone)

    assert own_phone.get("/auth/me").status_code == 200
    assert refresh(own_phone).status_code == 200


def test_an_activation_with_a_new_code_ends_the_older_sessions(app):
    lost_phone, admin = logged_in(app), logged_in(app, ADMIN_PHONE)
    code = admin.post(f"/admin/users/{RIDER_ID}/activation-code", headers=csrf_headers(admin)).get_json()["code"]

    activation = app.test_client().post("/auth/activate", json={"phone": RIDER_PHONE, "code": code, "password": NEW_PASSWORD})

    assert activation.status_code == 200
    assert lost_phone.get("/auth/me").status_code == 401


def test_a_token_without_session_version_is_refused(app, client):
    with app.app_context():
        token = create_access_token(identity=str(RIDER_ID), additional_claims={"role": "rider"})
    client.set_cookie("access_token_cookie", token)

    assert client.get("/auth/me").status_code == 401


# --- Suspension ----------------------------------------------------------------

def test_a_suspended_rider_loses_access_at_once(app):
    rider, admin = logged_in(app), logged_in(app, ADMIN_PHONE)

    set_status(admin, RIDER_ID, "suspended")

    assert rider.get("/rides?when=upcoming").status_code == 401
    assert refresh(rider).status_code == 401


def test_a_reactivated_account_does_not_revive_its_old_sessions(app):
    rider, admin = logged_in(app), logged_in(app, ADMIN_PHONE)
    set_status(admin, RIDER_ID, "suspended")

    set_status(admin, RIDER_ID, "active")

    assert rider.get("/auth/me").status_code == 401
    assert logged_in(app).get("/auth/me").status_code == 200


def test_a_suspended_admin_can_neither_reactivate_themselves_nor_create_an_admin(app):
    rogue, admin = logged_in(app, ADMIN_PHONE), other_admin(app)

    set_status(admin, ADMIN_ID, "suspended")

    assert set_status(rogue, ADMIN_ID, "active").status_code == 401
    created = rogue.post(
        "/admin/users",
        json={"role": "admin", "firstName": "Porte", "lastName": "Dérobée", "phone": "0694 22 22 22"},
        headers=csrf_headers(rogue),
    )
    assert created.status_code == 401


def test_an_admin_cannot_change_their_own_status(app):
    admin = logged_in(app, ADMIN_PHONE)

    response = set_status(admin, ADMIN_ID, "active")

    assert response.status_code == 422
    assert response.get_json()["detail"] == NOT_YOURSELF


def test_a_rider_still_cannot_change_a_status(app):
    rider = logged_in(app)

    assert set_status(rider, RIDER_ID, "active").status_code == 403
