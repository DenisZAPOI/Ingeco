"""
Shared test configuration.

Environment variables are set BEFORE importing the application: config.py
reads them when it is loaded. The tests use an in-memory SQLite database, so
they run without any database server.
"""

import os

import pytest
from flask import Blueprint, jsonify
from flask_pydantic_spec import Response

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("FLASK_SECRET_KEY", "test-key-long-enough-for-hs256-0123456789")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("LOG_FORMAT", "text")

from app.dtos.base import InputModel  # noqa: E402
from app.extensions import spec  # noqa: E402
from app.main import create_app  # noqa: E402
from app.utils.errors import Conflict  # noqa: E402


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
