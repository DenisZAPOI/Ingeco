"""
Application configuration, read from environment variables.

Nothing is hard-coded here: every value comes from the .env file, which is not
committed. Everyone can run the project with their own settings without
changing a line of code.
"""

import os
from datetime import timedelta

from dotenv import load_dotenv

# Loads the .env file of the BACKEND folder, if there is one.
load_dotenv()


class MissingConfiguration(RuntimeError):
    """Raised at startup when a required variable is missing."""


def _required(name: str) -> str:
    """Reads an environment variable, or fails with an explicit message.

    Failing at startup rather than on the first request: a server started with
    an incomplete configuration produces errors that are much harder to track.
    """
    value = os.getenv(name)
    if not value:
        raise MissingConfiguration(
            f"Missing environment variable: {name}.\n"
            f"Copy .env.example to .env and fill it in."
        )
    return value


def _optional(name: str, default: str) -> str:
    return os.getenv(name) or default


class Config:
    DATABASE_URL: str = _required("DATABASE_URL")
    SECRET_KEY: str = _required("FLASK_SECRET_KEY")

    # Explicit list: "*" is never allowed on an authenticated API.
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in _optional("CORS_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]

    DEBUG: bool = _optional("FLASK_DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = _optional("LOG_LEVEL", "INFO").upper()
    PORT: int = int(_optional("PORT", "5000"))

    # --- Authentication (Flask-JWT-Extended) ---------------------------------
    # Tokens live in HttpOnly cookies: JavaScript never reads them, so a
    # script injected in the page cannot steal them.
    JWT_SECRET_KEY: str = SECRET_KEY
    JWT_TOKEN_LOCATION: list[str] = ["cookies"]
    # Short access token: a suspended account loses access at the next
    # renewal. The long refresh token spares the user from typing the password.
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=30)
    # Persistent cookies: the session survives closing the browser.
    JWT_SESSION_COOKIE: bool = False
    # Safe by default: only an explicit "false" (local http) disables it.
    JWT_COOKIE_SECURE: bool = _optional("COOKIE_SECURE", "true").lower() != "false"
    JWT_COOKIE_SAMESITE: str = "Lax"
    # The refresh token is only sent to the route that uses it.
    JWT_REFRESH_COOKIE_PATH: str = "/auth/refresh"
    # Double-submit CSRF protection: a readable cookie holds a token that the
    # front-end copies into the X-CSRF-TOKEN header of every write request.
    JWT_COOKIE_CSRF_PROTECT: bool = True
