"""
Repositories: the ONLY place that talks to the database.

One file per resource, `<resource>_repository.py`. Each function receives the
session opened by the service, reads or writes, and returns models or plain
values. No business rule, no HTTP error.

As long as the DB team has not delivered the schema, a repository may return
fake data: switching to the real database then only changes this folder.

Template to copy: health_repository.py
"""
