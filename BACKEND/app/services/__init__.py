"""
Services: the business rules.

One file per domain, `<domain>_service.py`. A service checks who is allowed to
do what, which state transition is permitted (a ride can only be closed once
started), opens ONE transaction and calls the repositories.

It never imports Flask, never handles `request`, `jsonify` or status codes: it
raises an error from utils/errors.py instead. That is what makes it testable
without a server, and reusable by the WebSocket handlers.

Every service has its pytest tests.

Template to copy: health_service.py
"""
