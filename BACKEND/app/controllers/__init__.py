"""
Controllers: the HTTP entry point.

One file per resource, `<resource>_controller.py`, declaring a Flask Blueprint.
Remember to register it in main.py (app.register_blueprint).

A controller reads the request, calls ONE service, and returns the response
shaped by a DTO. It holds no business rule and no SQL.

Template to copy: health_controller.py
"""
