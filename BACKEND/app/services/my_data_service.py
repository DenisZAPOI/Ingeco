"""
« Mes données » : everything the application keeps about the logged-in person
(RGPD art. 15 and 20, audit RGPD R3), shown as a page and downloaded as a
JSON file by the front-end.

The rides are shown as the person sees them in the app (ride_service.present):
the same rules, nothing more of the other party.
"""

from dataclasses import dataclass
from datetime import datetime

from ..repository import deletion_repository, orientation_repository, ride_repository, support_repository
from ..repository.orientation_repository import SavedPlan
from ..repository.ride_repository import Ride
from ..repository.support_repository import SupportRequest
from ..repository.user_repository import User
from ..utils import database
from .account_rules import DRIVER, RIDER
from .auth_service import session_user
from .ride_service import present


@dataclass(frozen=True)
class MyData:
    user: User
    rides: list[Ride]
    # The current action plan and its answers (a rider who filled the questionnaire).
    plan: SavedPlan | None
    help_requests: list[SupportRequest]
    deletion_requested_at: datetime | None


def my_data(user_id: int) -> MyData:
    user = session_user(user_id)
    with database.session() as session:
        rides = _rides_of(session, user)
        plan = orientation_repository.latest_plan(session, user_id) if user.role == RIDER else None
        help_requests = support_repository.find_by_user(session, user_id)
        deletion_requested_at = deletion_repository.find_open(session, user_id)
    return MyData(
        user=user,
        rides=rides,
        plan=plan,
        help_requests=help_requests,
        deletion_requested_at=deletion_requested_at,
    )


def _rides_of(session, user: User) -> list[Ride]:
    if user.role == RIDER:
        rides = ride_repository.find_all_of(session, rider_id=user.id, driver_id=None)
    elif user.role == DRIVER:
        rides = ride_repository.find_all_of(session, rider_id=None, driver_id=user.id)
    else:
        return []
    return present(session, rides, user_id=user.id, role=user.role)
