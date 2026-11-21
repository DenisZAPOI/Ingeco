"""POST /help-requests/callback: « Être rappelé » (cahier des charges §6 and §7.1)."""

from sqlalchemy import select

from app.models import SupportRequestRow
from app.services.support_service import MAX_CALLBACKS_PER_ADDRESS
from tests.helpers import in_session
from tests.test_auth import csrf_headers, login

PHONE = "0694 12 34 56"


def requests():
    return in_session(lambda session: session.scalars(select(SupportRequestRow)).all())


def test_a_visitor_asks_to_be_called_back(client):
    response = client.post("/help-requests/callback", json={"phone": PHONE})

    assert response.status_code == 204
    [request] = requests()
    assert (request.kind, request.user_id, request.phone) == ("rappel", None, "+594694123456")
    assert request.handled_at is None


def test_a_logged_in_request_is_linked_to_the_account(client):
    user_id = login(client).get_json()["id"]

    response = client.post("/help-requests/callback", json={"phone": PHONE}, headers=csrf_headers(client))

    assert response.status_code == 204
    assert requests()[0].user_id == user_id


def test_a_logged_in_request_from_another_site_is_refused(client):
    """With a session cookie, the CSRF double submit is checked as on any other route."""
    login(client)

    assert client.post("/help-requests/callback", json={"phone": PHONE}).status_code == 401
    assert requests() == []


def test_an_invalid_number_is_refused(client):
    assert client.post("/help-requests/callback", json={"phone": "12"}).status_code == 400


def test_requests_are_limited_per_network_address(client):
    for _ in range(MAX_CALLBACKS_PER_ADDRESS):
        assert client.post("/help-requests/callback", json={"phone": PHONE}).status_code == 204

    response = client.post("/help-requests/callback", json={"phone": PHONE})

    assert response.status_code == 429
    assert len(requests()) == MAX_CALLBACKS_PER_ADDRESS
