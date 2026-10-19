"""
Business errors, turned into responses with a single format: { error, detail }.

A service raises one of these exceptions without knowing anything about HTTP;
the handlers registered in main.py turn it into a response with the right code.

Which code:
    400 BadRequest            invalid payload
    401 Unauthorized          missing, expired or invalid token
    403 Forbidden             the caller's role does not allow this action
    404 NotFound              resource missing, or invisible to the caller
    409 Conflict              conflict with the current STATE (ride already accepted)
    422 UnprocessableEntity   BUSINESS RULE violation (voucher exhausted)
    429 TooManyRequests       too many failed attempts (login, activation code)

The `detail` of a business error is shown as is to the user: write it in
French, in plain words.
"""

import json
import logging

from flask import Flask, Request, Response, jsonify
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class ApiError(Exception):
    code = 500
    error = "Internal Server Error"

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class BadRequest(ApiError):
    code = 400
    error = "Bad Request"


class Unauthorized(ApiError):
    code = 401
    error = "Unauthorized"


class Forbidden(ApiError):
    code = 403
    error = "Forbidden"


class NotFound(ApiError):
    code = 404
    error = "Not Found"


class Conflict(ApiError):
    code = 409
    error = "Conflict"


class UnprocessableEntity(ApiError):
    code = 422
    error = "Unprocessable Entity"


class TooManyRequests(ApiError):
    code = 429
    error = "Too Many Requests"


def register_handlers(app: Flask) -> None:
    """Every error leaves the API in the { error, detail } format.

    - Business error raised by a service → its own code and message.
    - Flask HTTP error (unknown route, wrong method…) → same format.
    - Any other exception → 500. The full trace goes to the logs; the client
      never gets the detail, which would expose the inside of the code.
    """

    @app.errorhandler(ApiError)
    def _business_error(error: ApiError):
        return jsonify({"error": error.error, "detail": error.detail}), error.code

    @app.errorhandler(HTTPException)
    def _http_error(error: HTTPException):
        return jsonify({"error": error.name, "detail": error.description}), error.code

    @app.errorhandler(Exception)
    def _unexpected_error(_error: Exception):
        logger.exception("Unhandled error")
        return jsonify({"error": "Internal Server Error", "detail": "Internal error."}), 500


# --- flask-pydantic-spec hooks -----------------------------------------------
# The library builds its own error responses; these two hooks rewrite them in
# our format, so the front-end only has one shape to read.

# Pydantic writes its messages in English; the front-end shows them next to the
# field, so the common ones are translated here. A message written by our own
# rules (type "business_rule", see dtos/base.py) is already in French.
BUSINESS_RULE_ERROR = "business_rule"
_FIELD_MESSAGES = {
    "missing": "Ce champ est obligatoire.",
    "extra_forbidden": "Ce champ n'est pas accepté.",
    "string_too_short": "Ce champ est obligatoire.",
    "string_too_long": "Ce texte est trop long.",
}
_DEFAULT_FIELD_MESSAGE = "Valeur invalide."


def _field_message(problem: dict) -> str:
    if problem["type"] == BUSINESS_RULE_ERROR:
        return problem["msg"]
    return _FIELD_MESSAGES.get(problem["type"], _DEFAULT_FIELD_MESSAGE)


def before_validation(_request: Request, response: Response | None, error: ValidationError | None, _view) -> None:
    """Invalid request body → 400 { error, detail: { fields: [...] } }."""
    if error is None or response is None:
        return
    fields = [
        {"field": ".".join(str(part) for part in problem["loc"]), "message": _field_message(problem)}
        for problem in error.errors()
    ]
    response.set_data(json.dumps({"error": "Bad Request", "detail": {"fields": fields}}, ensure_ascii=False))


def after_validation(_request: Request, response: Response, error: ValidationError | None, _view) -> None:
    """Response that does not match its DTO → 500.

    It is a bug in our code, not the client's: the documentation would announce
    a shape the route does not return.
    """
    if error is None:
        return
    logger.error("Response does not match its DTO", extra={"context": {"error": str(error)}})
    response.set_data(json.dumps({"error": "Internal Server Error", "detail": "Internal error."}))
