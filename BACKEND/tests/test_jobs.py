"""GET /jobs and GET /jobs/<id>: the job offers (module M2), on fake data.

Public routes: a visitor reads them without an account. Booking a trip to an
offer is a normal booking, with the place the offer gave.
"""

from app.repository import job_repository
from tests.test_auth import login
from tests.test_rides import book, booking, estimate

OFFLINE_OFFER_ID = 15


def test_a_visitor_reads_the_offers_without_an_account(client):
    response = client.get("/jobs")

    assert response.status_code == 200
    offers = response.get_json()["items"]
    assert len(offers) == len(job_repository.list_active(None, "fr"))
    assert {"title", "employer", "description", "contractType", "schedule", "beginnerWelcome"} <= offers[0].keys()


def test_the_offers_are_the_most_recent_first_and_name_their_commune(client):
    offers = client.get("/jobs").get_json()["items"]

    dates = [offer["publishedAt"] for offer in offers]
    assert dates == sorted(dates, reverse=True)
    assert {offer["communeName"] for offer in offers} == {"Cayenne", "Matoury", "Rémire-Montjoly"}


def test_an_offer_taken_offline_is_neither_listed_nor_readable(client):
    ids = [offer["id"] for offer in client.get("/jobs").get_json()["items"]]

    assert OFFLINE_OFFER_ID not in ids
    response = client.get(f"/jobs/{OFFLINE_OFFER_ID}")
    assert response.status_code == 404
    assert response.get_json()["detail"] == "Cette offre n'existe pas ou n'est plus en ligne."


def test_one_offer_is_read_by_its_id(client):
    first = client.get("/jobs").get_json()["items"][0]

    response = client.get(f"/jobs/{first['id']}")

    assert response.status_code == 200
    assert response.get_json() == first


def test_an_unknown_offer_is_not_found(client):
    assert client.get("/jobs/9999").status_code == 404


def test_comment_y_aller_books_a_trip_to_the_place_of_the_offer(client):
    """The signed place of an offer is accepted as the drop-off, unchanged."""
    offer = client.get("/jobs").get_json()["items"][0]
    login(client)

    response = book(client, booking(purpose="employment", dropoff=offer["place"]))

    assert response.status_code == 201
    assert response.get_json()["dropoff"]["address"] == offer["place"]["address"]


def test_the_place_of_an_offer_cannot_be_moved(client):
    """Same rule as GET /places (audit F9): a changed position loses its signature."""
    offer = client.get("/jobs").get_json()["items"][0]
    login(client)
    moved = offer["place"] | {"lat": offer["place"]["lat"] + 0.01}

    assert book(client, booking(dropoff=moved)).status_code == 422


def test_every_offer_is_inside_the_served_zone(client):
    """Until the other communes are in base (issue #52): every offer is bookable."""
    login(client)

    for offer in client.get("/jobs").get_json()["items"]:
        assert estimate(client, dropoff=offer["place"]).status_code == 200, offer["title"]


# --- Language of the contents (ADR 018) ----------------------------------------

def jobs_in(client, accept_language):
    return client.get("/jobs", headers={"Accept-Language": accept_language}).get_json()["items"]


def test_without_a_language_the_offers_are_in_french(client):
    offer = client.get("/jobs").get_json()["items"][0]

    assert offer["language"] == "fr"


def test_the_offers_follow_the_language_of_the_phone(client):
    french = {offer["id"]: offer for offer in jobs_in(client, "fr")}

    for language in ("en", "pt-BR"):
        for offer in jobs_in(client, language):
            assert offer["language"] == language
            assert offer["title"] != french[offer["id"]]["title"], (language, offer["title"])


def test_a_language_without_contents_falls_back_to_french(client):
    """The two creoles have no contents yet: French, and said so."""
    french = jobs_in(client, "fr")

    for language in ("gcr", "ht"):
        offers = jobs_in(client, language)
        assert [offer["title"] for offer in offers] == [offer["title"] for offer in french]
        assert {offer["language"] for offer in offers} == {"fr"}


def test_only_the_texts_change_with_the_language(client):
    """Same offers, same places: a trip booked in English goes to the same address."""
    french, english = jobs_in(client, "fr"), jobs_in(client, "en")

    assert [offer["place"] for offer in english] == [offer["place"] for offer in french]


def test_one_offer_is_read_in_the_language_of_the_phone(client):
    response = client.get("/jobs/5", headers={"Accept-Language": "pt-BR,pt;q=0.9,fr;q=0.5"})

    assert response.get_json()["title"] == "Vendedor(a) na feira"
    assert response.get_json()["language"] == "pt-BR"
