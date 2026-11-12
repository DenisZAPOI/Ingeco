"""
Settings refused at startup: they would expose a hosted server (audit F1, F7, F18).

Secure cookies (COOKIE_SECURE) mark a server reached over https: no public
demo accounts and no debug mode there, and never a weak signing key.
"""

import pytest

from app.config import Config, UnsafeConfiguration
from app.main import EXAMPLE_SECRET_KEY, check_safety, create_app

GOOD_KEY = "k" * 40


def settings(**values) -> type[Config]:
    """A configuration of the hosted server, changed by `values`."""
    defaults = {
        "SECRET_KEY": GOOD_KEY,
        "JWT_COOKIE_SECURE": True,
        "LOAD_DEMO_DATA": False,
        "DEBUG": False,
        "PERIODIC_TASKS_ENABLED": False,
    }
    return type("TestConfig", (Config,), defaults | values)


def test_a_hosted_configuration_starts():
    check_safety(settings())


@pytest.mark.parametrize("key", ["too-short", EXAMPLE_SECRET_KEY])
def test_a_weak_signing_key_is_refused(key):
    with pytest.raises(UnsafeConfiguration):
        check_safety(settings(SECRET_KEY=key, JWT_COOKIE_SECURE=False))


def test_the_demo_accounts_are_refused_over_https():
    with pytest.raises(UnsafeConfiguration):
        check_safety(settings(LOAD_DEMO_DATA=True))


def test_the_debug_mode_is_refused_over_https():
    with pytest.raises(UnsafeConfiguration):
        check_safety(settings(DEBUG=True))


def test_local_development_may_load_the_demo_in_debug():
    check_safety(settings(JWT_COOKIE_SECURE=False, LOAD_DEMO_DATA=True, DEBUG=True))


# --- Documentation and headers (audit F11, F12) -------------------------------

def test_the_documentation_is_off_by_default():
    application = create_app(settings(JWT_COOKIE_SECURE=False, API_DOCS_ENABLED=False))
    client = application.test_client()

    assert client.get("/apidoc/swagger").status_code == 404
    assert client.get("/apidoc/openapi.json").status_code == 404
    assert client.get("/health").status_code == 200


def test_the_answers_are_never_cached(client):
    assert client.get("/health").headers["Cache-Control"] == "no-store"


def test_https_asks_the_browser_to_stay_on_https():
    client = create_app(settings()).test_client()

    assert "max-age=" in client.get("/health").headers["Strict-Transport-Security"]


def test_plain_http_sends_no_hsts(client):
    assert "Strict-Transport-Security" not in client.get("/health").headers
