"""The log of a ride (table etape_course, migration 023): every step, when, and who did it.

The cahier des charges (§7.4) asks for the steps of a ride timestamped with
their author. The log is written in the same transaction as the change.
"""

from app.repository import ride_repository
from app.services import expiry_service
from tests.helpers import in_session
from tests.test_auth import DRIVER_PHONE, csrf_headers, login
from tests.test_drivers import act, go_online, waiting_ride
from tests.test_rides import book, booking

ALICE_ID, CHLOE_ID, ADMIN_ID = 1, 3, 6
ADMIN_PHONE = "0694 00 00 06"


def steps(ride_id: int) -> list[tuple[str, int | None]]:
    logged = in_session(lambda session: ride_repository.find_steps(session, ride_id))
    return [(step.kind, step.author_id) for step in logged]


def test_each_step_of_a_ride_is_logged_with_its_author(client):
    ride_id = waiting_ride(client)
    go_online(client)
    for action in ("accept", "release", "accept", "start", "complete"):
        assert act(client, ride_id, action).status_code == 200

    assert steps(ride_id) == [
        ("created", ALICE_ID),
        ("paid", ALICE_ID),
        ("accepted", CHLOE_ID),
        ("released", CHLOE_ID),
        ("accepted", CHLOE_ID),
        ("started", CHLOE_ID),
        ("completed", CHLOE_ID),
    ]


def test_a_cancellation_logs_its_author_and_the_refund(client):
    ride_id = waiting_ride(client)
    login(client, phone=ADMIN_PHONE)

    assert client.post(f"/rides/{ride_id}/cancel", headers=csrf_headers(client)).status_code == 200

    assert steps(ride_id)[-2:] == [("cancelled", ADMIN_ID), ("refunded", ADMIN_ID)]


def test_an_expiry_is_logged_without_author(client, clock):
    ride_id = waiting_ride(client)
    clock.move(minutes=16)

    expiry_service.expire_due_rides()

    assert steps(ride_id)[-2:] == [("expired", None), ("refunded", None)]


def test_a_refused_change_logs_nothing(client):
    login(client)
    ride_id = book(client, booking()).get_json()["id"]
    login(client, phone=DRIVER_PHONE)

    # Not paid yet: no driver can take it.
    assert act(client, ride_id, "accept").status_code == 409

    assert steps(ride_id) == [("created", ALICE_ID)]
