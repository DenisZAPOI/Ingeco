"""
Language of the contents sent back (job offers, later the help directory):
the one the phone asks for in Accept-Language, among those we have written.

The interface itself is translated by the front (ADR 013, 017); this only
concerns texts stored as data. Decision: docs/adr/018.
"""

from flask import request

DEFAULT_LANGUAGE = "fr"
# Same codes as the front (FRONTEND/src/i18n). The two creoles have no
# content yet: a phone set to "gcr" or "ht" gets French.
CONTENT_LANGUAGES = (DEFAULT_LANGUAGE, "en", "pt-BR")


def request_language() -> str:
    """The best language for this request, French when none fits."""
    return request.accept_languages.best_match(CONTENT_LANGUAGES, default=DEFAULT_LANGUAGE)
