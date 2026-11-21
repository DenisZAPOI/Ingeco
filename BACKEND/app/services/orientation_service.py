"""
Orientation questionnaire and action plan (module M1, cahier des charges §7.1).

Anyone may answer and see a plan, without an account: then nothing is kept
(minimisation, §2). A rider's answers and plan are kept, to find the plan
again and tick its steps. The plan is a proposal by simple rules
(orientation_rules.py): no automatic decision (GDPR art. 22).
"""

from ..repository import orientation_repository
from ..repository.orientation_repository import SavedPlan
from ..utils import database
from ..utils.errors import NotFound
from . import ride_rules
from .orientation_rules import Answers, build_plan, to_rows

NO_PLAN = "Vous n'avez pas encore de plan d'action. Répondez aux questions pour en avoir un."
NO_SUCH_STEP = "Cette étape n'existe pas dans votre plan."


def preview(answers: Answers) -> list[str]:
    """The steps of the plan, computed without keeping anything."""
    return build_plan(answers)


def save(rider_id: int, answers: Answers) -> SavedPlan:
    """Keeps the answers and their plan; it becomes the rider's current plan."""
    with database.session() as session:
        orientation_repository.save(session, rider_id, to_rows(answers), build_plan(answers), ride_rules.now())
        return _latest(session, rider_id)


def current(rider_id: int) -> SavedPlan:
    with database.session() as session:
        return _latest(session, rider_id)


def mark_step(rider_id: int, position: int, done: bool) -> SavedPlan:
    """Ticks (or unticks) a step of the current plan. Ticking it again keeps its first date."""
    with database.session() as session:
        plan = _latest(session, rider_id)
        step = next((step for step in plan.steps if step.position == position), None)
        if step is None:
            raise NotFound(NO_SUCH_STEP)
        if done != (step.done_at is not None):
            orientation_repository.set_step_done(session, plan.id, position, ride_rules.now() if done else None)
        return _latest(session, rider_id)


def _latest(session, rider_id: int) -> SavedPlan:
    plan = orientation_repository.latest_plan(session, rider_id)
    if plan is None:
        raise NotFound(NO_PLAN)
    return plan
