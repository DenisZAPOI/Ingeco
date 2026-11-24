"""Settings of the administrator (M9, P1): service hours, zones, tariff.

Each change applies to new requests only: rides already booked keep their
time, communes and price.
"""

import pytest

from tests.test_admin import OPERATOR_PHONE, as_admin
from tests.test_auth import DRIVER_PHONE, RIDER_PHONE, csrf_headers, login
from tests.test_rides import book, estimate
from tests.test_service_hours import cayenne

CAYENNE_ID, REMIRE_ID, MATOURY_ID = 1, 2, 3
PILOT_ZONE = [CAYENNE_ID, REMIRE_ID, MATOURY_ID]
COMMUNES_OF_FRENCH_GUIANA = 22


def week(**changes):
    """The 7 days open from 6 h to 20 h; changes: {weekday: (opens, closes) or None for closed}."""
    days = []
    for weekday in range(1, 8):
        hours = changes.get(f"day{weekday}", ("06:00", "20:00"))
        opens_at, closes_at = hours if hours else (None, None)
        days.append({"weekday": weekday, "opensAt": opens_at, "closesAt": closes_at})
    return {"days": days}


def put_hours(client, body):
    return client.put("/admin/service-hours", json=body, headers=csrf_headers(client))


def put_zones(client, commune_ids):
    return client.put("/admin/zones", json={"servedCommuneIds": commune_ids}, headers=csrf_headers(client))


def post_tariff(client, base_fare_cents, per_km_cents):
    body = {"baseFareCents": base_fare_cents, "perKmCents": per_km_cents}
    return client.post("/admin/tariff", json=body, headers=csrf_headers(client))


# --- Who may --------------------------------------------------------------------

@pytest.mark.parametrize("phone", [RIDER_PHONE, DRIVER_PHONE, OPERATOR_PHONE])
@pytest.mark.parametrize("path", ["/admin/service-hours", "/admin/zones", "/admin/tariff"])
def test_only_an_administrator_reads_the_settings(client, phone, path):
    login(client, phone=phone)

    assert client.get(path).status_code == 403


def test_only_an_administrator_changes_the_settings(client):
    login(client, phone=OPERATOR_PHONE)

    assert put_hours(client, week()).status_code == 403
    assert put_zones(client, PILOT_ZONE).status_code == 403
    assert post_tariff(client, 900, 90).status_code == 403


# --- Service hours ------------------------------------------------------------

def test_the_provisional_hours_are_every_day_all_day(client):
    as_admin(client)

    days = client.get("/admin/service-hours").get_json()["days"]

    assert [day["weekday"] for day in days] == [1, 2, 3, 4, 5, 6, 7]
    assert {(day["opensAt"], day["closesAt"]) for day in days} == {("00:00:00", "23:59:59")}


def test_the_administrator_sets_the_hours_of_the_week(client):
    as_admin(client)

    saved = put_hours(client, week(day7=None, day6=("08:00", "12:00")))

    assert saved.status_code == 200
    days = client.get("/admin/service-hours").get_json()["days"]
    assert (days[0]["opensAt"], days[0]["closesAt"]) == ("06:00:00", "20:00:00")
    assert (days[5]["opensAt"], days[5]["closesAt"]) == ("08:00:00", "12:00:00")
    assert (days[6]["opensAt"], days[6]["closesAt"]) == (None, None)


def test_a_closing_at_23_59_means_until_midnight(client):
    as_admin(client)

    days = put_hours(client, week(day1=("06:00", "23:59"))).get_json()["days"]

    assert days[0]["closesAt"] == "23:59:59"


def test_new_hours_apply_to_the_next_requests(client, clock):
    as_admin(client)
    put_hours(client, week())
    clock.current = cayenne(23, 21)  # Monday 21 h, closed from 20 h

    login(client)
    response = estimate(client)

    assert response.status_code == 422
    assert response.get_json()["detail"] == "Le service fonctionne le lundi de 6 h à 20 h. Choisissez une autre heure."


@pytest.mark.parametrize(
    "hours",
    [("20:00", "06:00"), ("08:00", "08:00"), ("08:00", None), (None, "20:00")],
)
def test_a_day_needs_an_opening_before_its_closing_or_nothing(client, hours):
    as_admin(client)

    response = put_hours(client, week(day1=hours))

    assert response.status_code == 400
    assert response.get_json()["detail"]["fields"][0]["field"] == "days.0"


def test_the_seven_days_are_sent_once_each(client):
    as_admin(client)
    body = week()
    body["days"][6]["weekday"] = 1

    assert put_hours(client, body).status_code == 400
    assert put_hours(client, {"days": week()["days"][:6]}).status_code == 400


def test_the_service_cannot_be_closed_every_day(client):
    as_admin(client)
    every_day_closed = week(**{f"day{weekday}": None for weekday in range(1, 8)})

    response = put_hours(client, every_day_closed)

    assert response.status_code == 422
    assert client.get("/admin/service-hours").get_json()["days"][0]["opensAt"] == "00:00:00"


# --- Zones -------------------------------------------------------------------

def test_the_zones_list_every_commune_with_the_pilot_zone_served(client):
    as_admin(client)

    items = client.get("/admin/zones").get_json()["items"]

    assert len(items) == COMMUNES_OF_FRENCH_GUIANA
    assert sorted(item["id"] for item in items if item["isServed"]) == PILOT_ZONE


def test_a_commune_no_longer_served_is_refused_to_new_requests(client):
    as_admin(client)

    saved = put_zones(client, [CAYENNE_ID, REMIRE_ID])

    assert saved.status_code == 200
    login(client)
    served_ids = [commune["id"] for commune in client.get("/communes").get_json()["items"]]
    assert served_ids == [CAYENNE_ID, REMIRE_ID]
    response = estimate(client)  # Cayenne to Matoury
    assert response.status_code == 422
    assert "Cayenne et Rémire-Montjoly" in response.get_json()["detail"]


def test_at_least_one_commune_stays_served(client):
    as_admin(client)

    assert put_zones(client, []).status_code == 422
    assert put_zones(client, [CAYENNE_ID, 999]).status_code == 422


# --- Tariff ------------------------------------------------------------------

def test_the_administrator_reads_the_active_tariff(client):
    as_admin(client)

    tariff = client.get("/admin/tariff").get_json()

    assert (tariff["baseFareCents"], tariff["perKmCents"]) == (800, 80)


def test_a_new_tariff_applies_to_new_bookings_and_old_rides_keep_their_price(client):
    login(client)
    booked = book(client).get_json()
    as_admin(client)

    created = post_tariff(client, 1000, 100)

    assert created.status_code == 201
    assert client.get("/admin/tariff").get_json()["id"] == created.get_json()["id"]
    login(client)
    assert estimate(client).get_json()["priceCents"] == 1000 + 100 * 13.1
    assert client.get(f"/rides/{booked['id']}").get_json()["priceCents"] == booked["priceCents"]


@pytest.mark.parametrize("amounts", [(-1, 80), (800, -1), (100_01, 80), (800, 10_01)])
def test_an_amount_out_of_bounds_is_refused(client, amounts):
    as_admin(client)

    assert post_tariff(client, *amounts).status_code == 400
