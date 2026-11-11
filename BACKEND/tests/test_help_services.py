"""GET /help-services and GET /help-services/<id>: the directory of help
services (module M5), on fake data.

Public routes: a visitor reads them without an account. Booking a trip to a
service is a normal booking, with the place the service gave.
"""

import re

from app.repository import help_service_repository
from tests.test_auth import login
from tests.test_rides import CAYENNE_TOWN_HALL, MATOURY_TOWN_HALL, book, booking, estimate

# National numbering plan of the ARCEP: 05 36 49 xx xx is reserved for fiction.
FICTION_PHONE = re.compile(r"^\+3353649\d{4}$")
FORBIDDEN_WORDS = ("diagnostic", "maladie mentale", "séjour", "nationalité")


def services_in(client, accept_language="fr"):
    return client.get("/help-services", headers={"Accept-Language": accept_language}).get_json()["items"]


def test_a_visitor_reads_the_directory_without_an_account(client):
    response = client.get("/help-services")

    assert response.status_code == 200
    services = response.get_json()["items"]
    assert len(services) == len(help_service_repository.list_services(None, "fr"))
    assert {
        "name", "category", "description", "hours", "place", "communeName",
        "phone", "wheelchairAccessible", "spokenLanguages", "updatedOn",
    } <= services[0].keys()


def test_every_need_of_the_cahier_des_charges_has_services(client):
    """§7.5: childcare, housing, rights, health, food, digital, paperwork, equipment."""
    categories = [service["category"] for service in services_in(client)]

    assert set(categories) == set(help_service_repository.CATEGORIES)


def test_the_services_are_grouped_by_need_in_the_order_of_the_cahier_des_charges(client):
    services = services_in(client)
    order = help_service_repository.CATEGORIES

    positions = [order.index(service["category"]) for service in services]
    assert positions == sorted(positions)


def test_every_service_is_fictitious_and_never_rings_at_someones(client):
    for service in services_in(client):
        assert "(fictif)" in service["name"], service["name"]
        assert FICTION_PHONE.match(service["phone"]), service["phone"]


def test_no_service_describes_an_illness_or_a_residence_status(client):
    """Cahier des charges §12: a need, never a diagnosis nor an administrative situation."""
    for service in services_in(client):
        text = f"{service['name']} {service['description']}".lower()
        assert not any(word in text for word in FORBIDDEN_WORDS), service["name"]


def test_every_service_says_what_the_cahier_des_charges_asks(client):
    """§7.5: spoken languages, hours, accessibility, date of update."""
    for service in services_in(client):
        assert service["spokenLanguages"], service["name"]
        assert "fr" in service["spokenLanguages"]
        assert service["hours"]
        assert isinstance(service["wheelchairAccessible"], bool)
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", service["updatedOn"])


def test_one_service_is_read_by_its_id(client):
    first = services_in(client)[0]

    response = client.get(f"/help-services/{first['id']}")

    assert response.status_code == 200
    assert response.get_json() == first


def test_an_unknown_service_is_not_found(client):
    response = client.get("/help-services/9999")

    assert response.status_code == 404
    assert response.get_json()["detail"] == "Ce service d'aide n'existe pas."


def test_comment_y_aller_books_a_trip_to_the_place_of_the_service(client):
    service = next(found for found in services_in(client) if found["category"] == "health")
    login(client)

    response = book(client, booking(purpose="health", pickup=MATOURY_TOWN_HALL, dropoff=service["place"]))

    assert response.status_code == 201
    assert response.get_json()["dropoff"]["address"] == service["place"]["address"]


def test_the_place_of_a_service_cannot_be_moved(client):
    """Same rule as GET /places (audit F9): a changed position loses its signature."""
    service = services_in(client)[0]
    login(client)
    moved = service["place"] | {"lng": service["place"]["lng"] + 0.01}

    assert book(client, booking(dropoff=moved)).status_code == 422


def test_every_service_is_inside_the_served_zone(client):
    """Until the other communes are in base (issue #52): every service is bookable."""
    login(client)

    for service in services_in(client):
        # From another commune: a service may stand next to the town hall used as pickup.
        pickup = MATOURY_TOWN_HALL if service["communeName"] != "Matoury" else CAYENNE_TOWN_HALL
        assert estimate(client, pickup=pickup, dropoff=service["place"]).status_code == 200, service["name"]


# --- Language of the contents (ADR 018) ----------------------------------------

def test_the_services_follow_the_language_of_the_phone(client):
    french = {service["id"]: service for service in services_in(client, "fr")}

    for language in ("en", "pt-BR"):
        for service in services_in(client, language):
            assert service["language"] == language
            assert service["name"] != french[service["id"]]["name"], (language, service["name"])
            assert service["hours"] != french[service["id"]]["hours"], (language, service["hours"])


def test_a_language_without_contents_falls_back_to_french(client):
    french = services_in(client, "fr")

    for language in ("gcr", "ht"):
        services = services_in(client, language)
        assert [service["name"] for service in services] == [service["name"] for service in french]
        assert {service["language"] for service in services} == {"fr"}


def test_only_the_texts_change_with_the_language(client):
    """Same services, same places, same order: a list read in English points to the same addresses."""
    french, english = services_in(client, "fr"), services_in(client, "en")

    assert [service["id"] for service in english] == [service["id"] for service in french]
    assert [service["place"] for service in english] == [service["place"] for service in french]
