"""
Session and access control, on the HTTP side.

The JWTs live in HttpOnly cookies set by Flask-JWT-Extended. This module is
the only one to handle them: controllers open and close a session with
start_session / end_session, and protect a route with @require_login.

The role check is done HERE, on the server. The front-end hides screens, it
protects nothing.
"""

import hmac
import logging
from collections.abc import Callable
from functools import wraps
from typing import Protocol

from flask import Response, current_app, g, jsonify, request
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

from .errors import Forbidden, Unauthorized

logger = logging.getLogger(__name__)

_ROLE_CLAIM = "role"
# Version of the account's sessions: changed by a new password or a
# suspension, it ends every session opened before (see check_account).
_SESSION_VERSION_CLAIM = "sv"
NOT_LOGGED_IN = "Vous devez vous connecter."
_ROLE_REFUSED = "Vous n'avez pas accès à cette action."


class SessionAccount(Protocol):
    id: int
    role: str
    session_version: int


# Rereads the account behind a token: raises Unauthorized if it may no longer
# use the app (suspended, removed, sessions ended). Set by create_app() with
# auth_service.check_session: utils/ does not import the services.
_check_account: Callable[[int, int | None], SessionAccount] | None = None


def configure(check_account: Callable[[int, int | None], SessionAccount]) -> None:
    global _check_account
    _check_account = check_account


def _claims(account: SessionAccount) -> dict:
    return {_SESSION_VERSION_CLAIM: account.session_version}


def start_session(response: Response, account: SessionAccount) -> None:
    """Sets the access and refresh cookies on the response."""
    renew_access(response, account)
    set_refresh_cookies(response, create_refresh_token(identity=str(account.id), additional_claims=_claims(account)))


def renew_access(response: Response, account: SessionAccount) -> None:
    """New access token only: the refresh token keeps its own expiry."""
    claims = _claims(account) | {_ROLE_CLAIM: account.role}
    set_access_cookies(response, create_access_token(identity=str(account.id), additional_claims=claims))


def end_session(response: Response) -> None:
    unset_jwt_cookies(response)


def check_logout_csrf() -> None:
    """Logging out must come from the app, not from a form of another site.

    It works without a valid token (an expired session is logged out too),
    so Flask-JWT-Extended does not check it: the double submit is checked
    here. Without the CSRF cookie, there is no session to end.
    """
    cookie = request.cookies.get(current_app.config["JWT_ACCESS_CSRF_COOKIE_NAME"])
    if cookie is None:
        return
    header = request.headers.get(current_app.config["JWT_ACCESS_CSRF_HEADER_NAME"], "")
    if not hmac.compare_digest(cookie, header):
        raise Unauthorized(NOT_LOGGED_IN)


def refresh_account() -> SessionAccount:
    """Checks the refresh token (and its CSRF header), then the account behind it."""
    verify_jwt_in_request(refresh=True)
    g.user_id = int(get_jwt_identity())
    return _account()


def require_login(*roles: str) -> Callable:
    """Route decorator: a valid access token, an account still allowed, and one of `roles` if given.

    The account is reread at every request (one read by primary key): a
    suspension or a new password ends the access at once, not when the
    15-minute token runs out.

    Place it ABOVE @spec.validate: an anonymous caller gets 401 before its
    body is even read.
    """

    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            # Read by request_logs: every log line names the caller.
            g.user_id = int(get_jwt_identity())
            account = _account()
            g.user_role = account.role
            if roles and account.role not in roles:
                raise Forbidden(_ROLE_REFUSED)
            return view(*args, **kwargs)

        return wrapper

    return decorator


def _account() -> SessionAccount:
    if _check_account is None:
        raise RuntimeError("access.configure(...) must be called at startup.")
    return _check_account(g.user_id, get_jwt().get(_SESSION_VERSION_CLAIM))


def current_user_id() -> int:
    """Id of the caller, inside a route protected by @require_login."""
    return g.user_id


def current_role() -> str:
    """Role of the caller, as stored now, inside a route protected by @require_login."""
    return g.user_role


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
