"""Administration of the accounts (UC51 to UC53): list, create, suspend, priority, vehicle, photo, code.

Farid (account 6) is the development administrator.
"""

import base64

import pytest

from app.services.admin_service import PAGE_SIZE, PHOTO_MAX_BYTES
from tests.test_auth import ADMIN_PHONE, DRIVER_PHONE, NEW_PASSWORD, RIDER_PHONE, csrf_headers, login
from tests.test_drivers import go_online, waiting_ride

ADMIN_ID, DRIVER_ID, RIDER_ID, PRIORITY_RIDER_ID, OPERATOR_PHONE = 6, 3, 1, 2, "0694 00 00 05"
# The smallest file that starts like a JPEG: the API checks the start, not the picture.
TINY_JPEG = b"\xff\xd8\xff\xe0" + b"0" * 100


def as_admin(client):
    login(client, phone=ADMIN_PHONE)


def new_driver(**changes):
    body = {
        "role": "driver",
        "firstName": "Joël",
        "lastName": "Exemple",
        "phone": "0694 55 55 55",
        "email": None,
        "vehicle": {"plate": " ab-123 -cd ", "model": "Véhicule fictif", "seats": 4, "isAccessible": False},
    }
    return body | changes


def create(client, body):
    return client.post("/admin/users", json=body, headers=csrf_headers(client))


def update(client, user_id, **body):
    return client.patch(f"/admin/users/{user_id}", json=body, headers=csrf_headers(client))


def accounts(client, **query):
    return client.get("/admin/users", query_string=query).get_json()


def put_photo(client, user_id, image=TINY_JPEG):
    body = {"imageBase64": base64.b64encode(image).decode()}
    return client.put(f"/admin/users/{user_id}/photo", json=body, headers=csrf_headers(client))


# ---------------------------------------------------------------------------
#  Access
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phone", [RIDER_PHONE, DRIVER_PHONE, OPERATOR_PHONE])
def test_only_an_administrator_reaches_the_accounts(client, phone):
    login(client, phone=phone)

    assert client.get("/admin/users").status_code == 403
    assert create(client, new_driver()).status_code == 403
    assert update(client, RIDER_ID, status="suspended").status_code == 403
    assert client.post(f"/admin/users/{RIDER_ID}/activation-code", headers=csrf_headers(client)).status_code == 403


def test_an_anonymous_caller_is_asked_to_log_in(client):
    assert client.get("/admin/users").status_code == 401


# ---------------------------------------------------------------------------
#  List and search (UC51)
# ---------------------------------------------------------------------------

def test_the_list_shows_the_newest_accounts_first_with_their_access(client):
    as_admin(client)

    items = accounts(client)["items"]

    assert [item["id"] for item in items] == [8, 7, 6, 5, 4, 3, 2, 1]
    to_activate = next(item for item in items if item["id"] == 7)
    assert (to_activate["isActivated"], to_activate["activationCodeExpiresAt"] is not None) == (False, True)


def test_the_list_is_filtered_by_role_and_status(client):
    as_admin(client)

    assert [item["id"] for item in accounts(client, role="rider", status="active")["items"]] == [7, 2, 1]
    assert [item["id"] for item in accounts(client, status="suspended")["items"]] == [8]


@pytest.mark.parametrize(
    ("search", "expected"),
    [("0694 00 00 03", [3]), ("694 00 00", [8, 7, 6, 5, 4, 3, 2, 1]), ("0694000001", [1]), ("chloe", [3]), ("DÉMO", [8, 7, 6, 5, 4, 3, 2, 1])],
)
def test_the_search_reads_a_phone_start_or_a_name(client, search, expected):
    as_admin(client)

    assert [item["id"] for item in accounts(client, search=search)["items"]] == expected


def test_the_list_comes_by_pages_without_repeating_an_account(client):
    as_admin(client)
    for number in range(PAGE_SIZE):
        create(client, new_driver(role="operator", phone=f"0694 70 00 {number:02d}", vehicle=None))

    first = accounts(client)
    second = accounts(client, cursor=first["nextCursor"])

    assert len(first["items"]) == PAGE_SIZE
    assert second["nextCursor"] is None
    ids = [item["id"] for item in first["items"] + second["items"]]
    assert len(ids) == len(set(ids)) == PAGE_SIZE + 8


def test_a_made_up_cursor_is_refused(client):
    as_admin(client)

    assert client.get("/admin/users?cursor=nimporte").status_code == 400


# ---------------------------------------------------------------------------
#  Creation (UC52) and activation code (UC53)
# ---------------------------------------------------------------------------

def test_an_administrator_creates_a_driver_who_activates_with_the_code(client):
    as_admin(client)

    response = create(client, new_driver())

    assert response.status_code == 201
    created = response.get_json()
    account, code = created["account"], created["activation"]["code"]
    assert (account["role"], account["phone"], account["isActivated"]) == ("driver", "+594694555555", False)
    assert account["vehicle"]["plate"] == "AB-123-CD"
    assert len(code) == 8 and code.isdigit()

    activated = client.post("/auth/activate", json={"phone": "0694 55 55 55", "code": code, "password": NEW_PASSWORD})
    assert activated.status_code == 200
    assert activated.get_json()["role"] == "driver"


def test_a_driver_needs_a_vehicle_and_an_operator_has_none(client):
    as_admin(client)

    assert create(client, new_driver(vehicle=None)).status_code == 422
    assert create(client, new_driver(role="operator")).status_code == 422
    assert create(client, new_driver(role="operator", vehicle=None)).status_code == 201


def test_a_partner_referent_cannot_be_created_yet(client):
    as_admin(client)

    assert create(client, new_driver(role="partner", vehicle=None)).status_code == 400


def test_a_phone_or_a_plate_already_used_is_refused(client):
    as_admin(client)

    same_phone = create(client, new_driver(phone=DRIVER_PHONE))
    same_plate = create(client, new_driver(vehicle=new_driver()["vehicle"] | {"plate": "AA-001-AA"}))

    assert (same_phone.status_code, same_plate.status_code) == (409, 409)
    assert "immatriculation" in same_plate.get_json()["detail"]


def test_a_new_code_replaces_the_previous_one(client):
    as_admin(client)
    first = create(client, new_driver()).get_json()
    user_id = first["account"]["id"]

    second = client.post(f"/admin/users/{user_id}/activation-code", headers=csrf_headers(client))

    assert second.status_code == 201
    old = {"phone": "0694 55 55 55", "code": first["activation"]["code"], "password": NEW_PASSWORD}
    assert client.post("/auth/activate", json=old).status_code == 422
    new = old | {"code": second.get_json()["code"]}
    assert client.post("/auth/activate", json=new).status_code == 200


def test_a_code_for_a_forgotten_password(client):
    as_admin(client)

    code = client.post(f"/admin/users/{RIDER_ID}/activation-code", headers=csrf_headers(client)).get_json()["code"]

    assert client.post("/auth/activate", json={"phone": RIDER_PHONE, "code": code, "password": NEW_PASSWORD}).status_code == 200
    assert login(client, password=NEW_PASSWORD).status_code == 200


def test_the_code_never_reaches_the_logs(client, caplog):
    as_admin(client)

    code = create(client, new_driver()).get_json()["activation"]["code"]

    assert code not in caplog.text


# ---------------------------------------------------------------------------
#  Changes (UC51)
# ---------------------------------------------------------------------------

def test_a_suspended_account_cannot_log_in_and_comes_back_when_reactivated(client):
    as_admin(client)

    assert update(client, RIDER_ID, status="suspended").get_json()["status"] == "suspended"
    assert login(client).status_code == 403

    as_admin(client)
    update(client, RIDER_ID, status="active")
    assert login(client).status_code == 200


def test_an_administrator_cannot_suspend_their_own_account(client):
    as_admin(client)

    assert update(client, ADMIN_ID, status="suspended").status_code == 422


def test_a_suspended_driver_goes_offline_and_cannot_come_back_online(client):
    go_online(client)
    as_admin(client)

    suspended = update(client, DRIVER_ID, status="suspended").get_json()

    assert suspended["isAvailable"] is False
    # Their 15-minute token is still valid: it must not be enough.
    assert go_online(client).status_code == 403


def test_a_driver_holding_a_ride_cannot_be_suspended(client):
    ride_id = waiting_ride(client)
    go_online(client)
    client.post(f"/rides/{ride_id}/accept", headers=csrf_headers(client))
    as_admin(client)

    response = update(client, DRIVER_ID, status="suspended")

    assert response.status_code == 409
    assert "course" in response.get_json()["detail"]


def test_only_a_rider_is_priority_and_only_a_driver_has_a_vehicle(client):
    as_admin(client)
    vehicle = {"plate": "ZZ-999-ZZ", "model": "Autre véhicule", "seats": 6, "isAccessible": True}

    assert update(client, RIDER_ID, isPriority=True).get_json()["isPriority"] is True
    assert update(client, DRIVER_ID, isPriority=True).status_code == 422
    assert update(client, DRIVER_ID, vehicle=vehicle).get_json()["vehicle"]["seats"] == 6
    assert update(client, RIDER_ID, vehicle=vehicle).status_code == 422


def test_null_is_not_a_change(client):
    as_admin(client)

    assert update(client, RIDER_ID, status=None).status_code == 400


def test_an_unknown_account_is_not_found(client):
    as_admin(client)

    assert update(client, 999, status="suspended").status_code == 404
    assert client.get("/admin/users/999").status_code == 404


# ---------------------------------------------------------------------------
#  Photo of a driver
# ---------------------------------------------------------------------------

def test_an_administrator_saves_and_reads_back_a_driver_photo(client):
    as_admin(client)

    saved = put_photo(client, DRIVER_ID)
    photo = client.get(f"/admin/users/{DRIVER_ID}/photo")

    assert saved.status_code == 200
    assert saved.get_json()["photoUpdatedAt"] is not None
    assert (photo.status_code, photo.mimetype, photo.data) == (200, "image/jpeg", TINY_JPEG)


def test_a_photo_must_be_a_small_jpeg_of_a_driver(client):
    as_admin(client)

    assert put_photo(client, DRIVER_ID, b"\x89PNG not a jpeg").status_code == 422
    assert put_photo(client, DRIVER_ID, TINY_JPEG + b"0" * PHOTO_MAX_BYTES).status_code in (400, 422)
    assert put_photo(client, RIDER_ID).status_code == 422
    assert client.get(f"/admin/users/{DRIVER_ID}/photo").status_code == 404
