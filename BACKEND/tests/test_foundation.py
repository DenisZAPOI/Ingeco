"""
Foundation tests: they check the architecture keeps its promises before the
first feature.

Feature tests go in this folder, one file per resource. Each access rule gets
a test proving that an unauthorized user is refused.
"""

from app.services import health_service
from app.services.health_service import DatabaseUnreachable


# ---------------------------------------------------------------------------
#  The whole chain works
# ---------------------------------------------------------------------------

def test_health_goes_through_every_layer_down_to_the_database(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": {"reachable": True, "dialect": "sqlite"}}


def test_health_switches_to_503_without_leaking_technical_details(client, monkeypatch):
    def database_down():
        raise DatabaseUnreachable

    monkeypatch.setattr(health_service, "database_state", database_down)
    response = client.get("/health")

    assert response.status_code == 503
    assert response.get_json()["database"] == {"reachable": False, "dialect": None}


# ---------------------------------------------------------------------------
#  API conventions are kept
# ---------------------------------------------------------------------------

def test_a_business_error_becomes_a_response_in_the_error_format(client):
    response = client.get("/_tests/business-error")

    assert response.status_code == 409
    assert response.get_json() == {"error": "Conflict", "detail": "This ride has already been accepted."}


def test_an_invalid_body_is_refused_with_400_and_the_faulty_fields(client):
    response = client.post("/_tests/validation", json={"pickupAddress": "Cayenne"})

    assert response.status_code == 400
    body = response.get_json()
    assert body["error"] == "Bad Request"
    assert [field["field"] for field in body["detail"]["fields"]] == ["seats"]


def test_an_unknown_field_is_refused(client):
    response = client.post("/_tests/validation", json={"pickupAddress": "Kourou", "seats": 1, "price": 0})

    assert response.status_code == 400


def test_a_response_not_matching_its_dto_is_a_500(client):
    assert client.get("/_tests/non-matching-response").status_code == 500


def test_an_unexpected_error_leaks_nothing(client):
    response = client.get("/_tests/unexpected-error")

    assert response.status_code == 500
    assert "internal detail" not in response.get_data(as_text=True)


def test_an_unknown_route_answers_in_the_error_format(client):
    response = client.get("/unknown-route")

    assert response.status_code == 404
    assert set(response.get_json()) == {"error", "detail"}


def test_every_response_carries_a_request_id(client):
    assert len(client.get("/health").headers.get("X-Request-Id", "")) == 12


def test_cors_only_allows_the_front_end(client):
    allowed = client.get("/health", headers={"Origin": "http://localhost:5173"})
    refused = client.get("/health", headers={"Origin": "http://malicious.example"})

    assert allowed.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173"
    assert "Access-Control-Allow-Origin" not in refused.headers


def test_the_browser_keeps_the_cors_preflight(client):
    response = client.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert response.headers.get("Access-Control-Max-Age") == "7200"


def test_the_openapi_description_is_served(client):
    response = client.get("/apidoc/openapi.json")

    assert response.status_code == 200
    assert "/health" in response.get_json()["paths"]
