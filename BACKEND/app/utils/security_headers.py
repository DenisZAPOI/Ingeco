"""
Security headers set on every response.

The API only returns JSON and loads nothing: the strictest content policy fits.
The Swagger page (/apidoc, development only) loads its scripts from a CDN, so
it keeps the browser's default policy.
"""

from flask import Flask, Response, request

_DOCUMENTATION_PREFIX = "/apidoc"
# A year, the usual value: the browser then refuses plain http for the API.
HSTS_MAX_AGE_SECONDS = 365 * 24 * 60 * 60


def install(app: Flask, *, https: bool) -> None:
    @app.after_request
    def _set_headers(response: Response) -> Response:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        if not request.path.startswith(_DOCUMENTATION_PREFIX):
            response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        # Answers hold personal data, and activation codes: never kept by the
        # browser nor a proxy. A route that may be cached (the driver's photo)
        # sets its own Cache-Control.
        if "Cache-Control" not in response.headers:
            response.headers["Cache-Control"] = "no-store"
        if https:
            response.headers["Strict-Transport-Security"] = f"max-age={HSTS_MAX_AGE_SECONDS}"
        return response
