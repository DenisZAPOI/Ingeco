"""
Security headers set on every response.

The API only returns JSON and loads nothing: the strictest content policy fits.
The Swagger page (/apidoc) loads its scripts from a CDN, so it keeps the
browser's default policy.
"""

from flask import Flask, Response, request

_DOCUMENTATION_PREFIX = "/apidoc"


def install(app: Flask) -> None:
    @app.after_request
    def _set_headers(response: Response) -> Response:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        if not request.path.startswith(_DOCUMENTATION_PREFIX):
            response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        return response
