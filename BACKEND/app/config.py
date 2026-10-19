"""
Application configuration, read from environment variables.

Nothing is hard-coded here: every value comes from the .env file, which is not
committed. Everyone can run the project with their own settings without
changing a line of code.
"""

import os

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
