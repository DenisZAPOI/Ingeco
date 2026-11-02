"""GET /communes and GET /places: the served zone and the address search.

Without ORS_API_KEY (forced empty in conftest.py), the search uses the fake
places. The OpenRouteService tests replace the network call by a fake answer.
"""

import pytest

from app.repository import place_repository
from app.repository.place_repository import PlacesUnavailable
from tests.test_auth import login

CAYENNE, MATOURY = 1, 3


def search(client, text, commune_id=CAYENNE):
    return client.get("/places", query_string={"search": text, "communeId": commune_id})


def test_the_served_communes_are_those_of_the_pilot(client):
    login(client)

    names = [commune["name"] for commune in client.get("/communes").get_json()["items"]]

    assert names == ["Cayenne", "Matoury", "Rémire-Montjoly"]


def test_the_search_ignores_accents_and_stays_in_the_commune(client):
    login(client)

    labels = [place["label"] for place in search(client, "aeroport eboue", MATOURY).get_json()["items"]]

    assert labels == ["Aéroport Félix Éboué, Matoury"]
    assert search(client, "aeroport", CAYENNE).get_json()["items"] == []


def test_a_search_of_one_letter_is_refused(client):
    login(client)

    response = search(client, "a")

    assert response.status_code == 400
    assert response.get_json()["detail"]["fields"][0]["field"] == "search"


def test_a_commune_outside_the_zone_is_refused(client):
    login(client)

    response = search(client, "mairie", 99)

    assert response.status_code == 422
    assert "Nous ne desservons pas encore" in response.get_json()["detail"]


def test_an_anonymous_caller_cannot_search(client):
    assert client.get("/communes").status_code == 401
    assert search(client, "mairie").status_code == 401


# --- OpenRouteService ----------------------------------------------------------

def _feature(label, locality, localadmin=None, lng=-52.33, lat=4.85):
    return {
        "geometry": {"coordinates": [lng, lat]},
        "properties": {"label": label, "locality": locality, "localadmin": localadmin},
    }


@pytest.fixture
def ors(monkeypatch):
    """A key is set, and each call answers with what the test puts in `answers`."""
    answers = []
    calls = []

    def fake_call(method, path, data):
        calls.append((method, path, data))
        answer = answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr(place_repository, "_api_key", "test-key")
    monkeypatch.setattr(place_repository, "_call_ors", fake_call)
    return answers, calls


def test_ors_results_outside_the_chosen_commune_are_dropped(client, ors):
    answers, _ = ors
    answers.append({
        "features": [
            _feature("Mairie de Matoury", "Matoury", lat=4.847, lng=-52.331),
            _feature("Mairie de Cayenne", "Cayenne"),
            _feature("Rue des Écoles, Larivot", None, localadmin="Matoury"),
        ]
    })
    login(client)

    places = search(client, "mairie", MATOURY).get_json()["items"]

    assert [place["label"] for place in places] == ["Mairie de Matoury", "Rue des Écoles, Larivot"]
    assert (places[0]["lat"], places[0]["lng"], places[0]["communeId"]) == (4.847, -52.331, MATOURY)


def test_ors_down_during_a_search_answers_503(client, ors):
    answers, _ = ors
    answers.append(PlacesUnavailable("timeout"))
    login(client)

    response = search(client, "mairie")

    assert response.status_code == 503
    assert "ne répond pas" in response.get_json()["detail"]


def test_the_road_distance_comes_from_ors_in_kilometres(ors):
    answers, calls = ors
    answers.append({"routes": [{"summary": {"distance": 11_437.2}}]})

    assert place_repository.road_distance_km(4.93, -52.32, 4.84, -52.33) == pytest.approx(11.4372)
    # ORS takes positions as [longitude, latitude].
    assert calls[0][2] == {"coordinates": [[-52.32, 4.93], [-52.33, 4.84]]}
