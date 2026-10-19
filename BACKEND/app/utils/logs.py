"""
Application logging.

DESTINATION: standard output, not a file. Read by the terminal, by Docker and
by any hosting platform, with no rotation to manage.

FORMAT: one JSON line per event, so logs can be filtered (every refused access
for a given user, for instance). LOG_FORMAT=text switches back to a
human-readable format in development.

NEVER log: password, token, Authorization header, e-mail, phone number,
address or position of a user (GDPR). Log the user id, not their identity.
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Serializes each record as one JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Business context given with logger.info("...", extra={"context": {...}})
        context = getattr(record, "context", None)
        if context:
            payload["context"] = context

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def configure(level: str = "INFO") -> None:
    """Installs logging on standard output."""
    handler = logging.StreamHandler(sys.stdout)

    if os.getenv("LOG_FORMAT", "json").lower() == "text":
        handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s %(name)s  %(message)s"))
    else:
        handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Werkzeug already logs every request: keep it quiet so it does not
    # drown the application messages.
    logging.getLogger("werkzeug").setLevel("WARNING")
