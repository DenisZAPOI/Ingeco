"""
Real-time channel (Flask-SocketIO): the status of a ride and the drivers'
offers, updated without pressing "Actualiser". No position of the driver: GPS
tracking is out of scope (specification §5).

- handlers.py   events received: connection, subscriptions (ride:follow, offers:follow);
- broadcast.py  events sent by the services, once their transaction is committed.

This file imports neither: the services import broadcast.py, and handlers.py
imports the services. Without imports here, there is no import cycle.
"""
