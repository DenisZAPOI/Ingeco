"""
Shared test configuration.

Environment variables are set BEFORE importing the application: config.py
reads them when it is loaded. The tests use an in-memory SQLite database, so
they run without any database server.
"""

import os
from datetime import datetime, timedelta, timezone

import pytest
from flask import Blueprint, jsonify
from flask_pydantic_spec import Response

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("FLASK_SECRET_KEY", "test-key-long-enough-for-hs256-0123456789")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("LOG_FORMAT", "text")
# The test client speaks http: Secure cookies would never be sent back.
os.environ.setdefault("COOKIE_SECURE", "false")
# Forced, not a default: a developer's key in .env must not make the tests
# call OpenRouteService.
os.environ["ORS_API_KEY"] = ""
# The tests run the expiry themselves, after moving the clock.
os.environ["PERIODIC_TASKS_ENABLED"] = "false"
# Forced: each test loads the development accounts itself (fresh_state).
os.environ["LOAD_DEMO_DATA"] = "false"
os.environ.setdefault("API_DOCS_ENABLED", "true")

from app.dtos.base import InputModel  # noqa: E402
from app.extensions import spec  # noqa: E402
from app.main import create_app  # noqa: E402
from app.repository import registration_repository, ride_repository, user_repository  # noqa: E402
from app.services import auth_service, place_service, ride_rules, user_service  # noqa: E402
from app.utils.access import require_login  # noqa: E402
from app.utils.errors import Conflict  # noqa: E402

# Signed stops are built at import time by the test modules (tests/test_rides.py).
place_service.configure(signing_key=os.environ["FLASK_SECRET_KEY"])


class TestBody(InputModel):
    __test__ = False  # not a pytest test class, despite its name

    pickup_address: str
    seats: int


def _test_routes() -> Blueprint:
    """Routes that only exist during the tests, to check the plumbing."""
    blueprint = Blueprint("tests", __name__, url_prefix="/_tests")

    @blueprint.get("/business-error")
    def business_error():
        raise Conflict("This ride has already been accepted.")

    @blueprint.post("/validation")
    @spec.validate(body=TestBody, resp=Response(HTTP_204=None))
    def validation():
        return "", 204

    @blueprint.get("/non-matching-response")
    @spec.validate(resp=Response(HTTP_200=TestBody))
    def non_matching_response():
        return jsonify({"pickupAddress": "no seats field"}), 200

    @blueprint.get("/admin-only")
    @require_login("admin")
    def admin_only():
        return "", 204

    @blueprint.get("/unexpected-error")
    def unexpected_error():
        raise RuntimeError("internal detail that must never leak")

    return blueprint


@pytest.fixture(scope="session")
def app():
    application = create_app()
    application.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)
    application.register_blueprint(_test_routes())
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def fresh_state():
    """Every test starts from the development accounts, no ride (not even the development ones), and no failed attempt counted."""
    user_repository.reset(demo_accounts=True)
    ride_repository.reset(dev_rides=False)
    auth_service.login_attempts.clear()
    auth_service.activation_attempts.clear()
    auth_service.registration_codes_by_phone.clear()
    auth_service.registration_codes_by_address.clear()
    auth_service.login_attempts_by_address.clear()
    auth_service.activation_attempts_by_address.clear()
    user_service.current_password_attempts.clear()
    place_service.lookups.clear()
    registration_repository.reset()
    # Registrations get the fixed demo code: the tests type it.
    auth_service.configure(demo_codes=True)


@pytest.fixture
def clock(monkeypatch):
    """Moves the API's clock: clock.move(minutes=16)."""

    class Clock:
        current = datetime.now(timezone.utc)

        def move(self, **delta):
            self.current += timedelta(**delta)

    fake = Clock()
    monkeypatch.setattr(ride_rules, "now", lambda: fake.current)
    return fake
