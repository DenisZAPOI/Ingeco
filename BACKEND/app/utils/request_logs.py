"""
One log line per HTTP request: method, path, status, duration, user, and a
request id. The id is also sent back in the `X-Request-Id` header: when the
front-end shows an error, the matching log line can be found.

401 and 403 responses are logged as WARNING: they are the security events.
The request body is NEVER logged (it may hold a password or personal data).
"""

import logging
import time
import uuid

from flask import Flask, Response, g, request

logger = logging.getLogger("requests")

_SECURITY_CODES = {401, 403}
_REQUEST_ID_LENGTH = 12


def install(app: Flask) -> None:
    @app.before_request
    def _start() -> None:
        g.request_id = uuid.uuid4().hex[:_REQUEST_ID_LENGTH]
        g.request_start = time.perf_counter()

    @app.after_request
    def _end(response: Response) -> Response:
        duration_ms = round((time.perf_counter() - g.get("request_start", time.perf_counter())) * 1000, 1)
        context = {
            "requestId": g.get("request_id"),
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "durationMs": duration_ms,
            # Filled in by the authentication layer once it exists.
            "userId": g.get("user_id"),
        }

        if response.status_code in _SECURITY_CODES:
            logger.warning("Access refused", extra={"context": context})
        elif response.status_code >= 500:
            logger.error("Request failed", extra={"context": context})
        else:
            logger.info("Request handled", extra={"context": context})

        response.headers["X-Request-Id"] = g.get("request_id", "")
        return response
