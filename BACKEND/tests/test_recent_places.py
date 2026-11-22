"""GET /places/recent: the last places of the rider's own rides.

Alice's rides in sql/demo-data.sql, the most recently booked first: ride 3
(1 rue Fictive, Cayenne → organisme de formation, Rémire-Montjoly), then
rides 7, 6, 5 (mairie de Cayenne → mairie de Matoury), 4 and 1.
"""

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models import Commune
from app.services.place_service import MAX_RECENT_PLACES
from tests.test_auth import DRIVER_PHONE, csrf_headers, login

REMIRE_MONTJOLY = 2


def recent_places(client) -> list[dict]:
    return client.get("/places/recent").get_json()["items"]


def as_stop(place: dict) -> dict:
    return {"address": place["label"], "lat": place["lat"], "lng": place["lng"], "communeId": place["communeId"],
            "token": place["token"]}


def test_the_last_distinct_places_come_first(client):
    login(client)

    labels = [place["label"] for place in recent_places(client)]

    assert labels == [
        "1 rue Fictive, Cayenne",
        "Organisme de formation fictif, Rémire-Montjoly",
        "Mairie de Cayenne",
    ]
    assert len(labels) == MAX_RECENT_PLACES


def test_a_recent_place_can_be_booked_again_as_is(client):
    login(client)
    # The first and the third (mairie de Cayenne) have the same position in
    # demo-data.sql: the estimate would refuse them as the same place.
    pickup, dropoff, _ = recent_places(client)

    response = client.post(
        "/rides/estimate", json={"pickup": as_stop(pickup), "dropoff": as_stop(dropoff)}, headers=csrf_headers(client)
    )

    assert response.status_code == 200


def test_a_place_of_a_commune_no_longer_served_is_left_out(client, test_database):
    login(client)
    # Reference data: demo-data.sql does not reset it, so it is put back here.
    with Session(test_database) as session:
        session.execute(update(Commune).where(Commune.id == REMIRE_MONTJOLY).values(is_served=False))
        session.commit()
    try:
        labels = [place["label"] for place in recent_places(client)]
    finally:
        with Session(test_database) as session:
            session.execute(update(Commune).where(Commune.id == REMIRE_MONTJOLY).values(is_served=True))
            session.commit()

    assert "Organisme de formation fictif, Rémire-Montjoly" not in labels
    assert labels[:2] == ["1 rue Fictive, Cayenne", "Mairie de Cayenne"]


def test_a_driver_is_refused(client):
    login(client, DRIVER_PHONE)

    assert client.get("/places/recent").status_code == 403


def test_an_anonymous_caller_is_refused(client):
    assert client.get("/places/recent").status_code == 401
