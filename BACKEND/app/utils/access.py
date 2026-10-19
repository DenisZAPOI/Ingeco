"""
Session and access control, on the HTTP side.

The JWTs live in HttpOnly cookies set by Flask-JWT-Extended. This module is
the only one to handle them: controllers open and close a session with
start_session / end_session, and protect a route with @require_login.

The role check is done HERE, on the server. The front-end hides screens, it
protects nothing.
"""

import logging
from collections.abc import Callable
from functools import wraps

from flask import Response, g, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    verify_jwt_in_request,
)

from .errors import Forbidden

logger = logging.getLogger(__name__)

_ROLE_CLAIM = "role"
NOT_LOGGED_IN = "Vous devez vous connecter."
_ROLE_REFUSED = "Vous n'avez pas accès à cette action."


def start_session(response: Response, user_id: int, role: str) -> None:
    """Sets the access and refresh cookies on the response."""
    set_access_cookies(response, create_access_token(identity=str(user_id), additional_claims={_ROLE_CLAIM: role}))
    set_refresh_cookies(response, create_refresh_token(identity=str(user_id)))


def renew_access(response: Response, user_id: int, role: str) -> None:
    """New access token only: the refresh token keeps its own expiry."""
    set_access_cookies(response, create_access_token(identity=str(user_id), additional_claims={_ROLE_CLAIM: role}))


def end_session(response: Response) -> None:
    unset_jwt_cookies(response)


def refresh_identity() -> int:
    """Checks the refresh token (and its CSRF header) and returns the user id."""
    verify_jwt_in_request(refresh=True)
    user_id = int(get_jwt_identity())
    g.user_id = user_id
    return user_id


def require_login(*roles: str) -> Callable:
    """Route decorator: a valid access token, and one of `roles` if given.

    Place it ABOVE @spec.validate: an anonymous caller gets 401 before its
    body is even read.
    """

    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            # Read by request_logs: every log line names the caller.
            g.user_id = int(get_jwt_identity())
            if roles and get_jwt().get(_ROLE_CLAIM) not in roles:
                raise Forbidden(_ROLE_REFUSED)
            return view(*args, **kwargs)

        return wrapper

    return decorator


def current_user_id() -> int:
    """Id of the caller, inside a route protected by @require_login."""
    return g.user_id


def register_jwt_callbacks(jwt: JWTManager) -> None:
    """Token problems answer in the { error, detail } format, in French.

    The technical reason (expired, bad signature, missing CSRF header…) goes to
    the logs only.
    """

    def _refused(reason: str):
        logger.info("Token refused", extra={"context": {"reason": reason}})
        return jsonify({"error": "Unauthorized", "detail": NOT_LOGGED_IN}), 401

    jwt.unauthorized_loader(_refused)
    jwt.invalid_token_loader(_refused)
    jwt.expired_token_loader(lambda _header, _payload: _refused("expired token"))
