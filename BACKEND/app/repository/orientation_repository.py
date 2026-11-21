"""
Orientation (module M1): tables questionnaire, reponse_questionnaire,
plan_action and etape_plan of the DB team (migration 017, issue #50).

Every filling is kept; the most recent one counts (index
idx_questionnaire_usager). A step never names an offer nor a service here:
the plan leads to lists the person filters herself, so id_offre and
id_service stay NULL.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..models import ActionPlanRow, AnswerRow, PlanStepRow, QuestionnaireRow


@dataclass(frozen=True)
class PlanStep:
    position: int
    code: str
    done_at: datetime | None


@dataclass(frozen=True)
class SavedPlan:
    id: int
    created_at: datetime
    # (question, answer, text) rows of the questionnaire behind the plan.
    answers: list[tuple[str, str, str | None]]
    steps: list[PlanStep]


def save(
    session: Session,
    rider_id: int,
    answers: list[tuple[str, str, str | None]],
    steps: list[str],
    now: datetime,
) -> int:
    """Writes one filling and its plan; returns the id of the plan."""
    questionnaire = QuestionnaireRow(rider_id=rider_id, filled_at=now)
    session.add(questionnaire)
    session.flush()
    session.add_all(
        AnswerRow(questionnaire_id=questionnaire.id, question_code=question, answer_code=answer, text=text)
        for question, answer, text in answers
    )
    plan = ActionPlanRow(questionnaire_id=questionnaire.id, created_at=now)
    session.add(plan)
    session.flush()
    session.add_all(PlanStepRow(plan_id=plan.id, position=index, step_code=code) for index, code in enumerate(steps, 1))
    session.flush()
    return plan.id


def latest_plan(session: Session, rider_id: int) -> SavedPlan | None:
    """The plan of the rider's most recent questionnaire, or None."""
    found = session.execute(
        select(ActionPlanRow, QuestionnaireRow.id)
        .join(QuestionnaireRow, QuestionnaireRow.id == ActionPlanRow.questionnaire_id)
        .where(QuestionnaireRow.rider_id == rider_id)
        # Same second twice (a double tap): the last written wins.
        .order_by(QuestionnaireRow.filled_at.desc(), QuestionnaireRow.id.desc())
        .limit(1)
    ).first()
    if found is None:
        return None
    plan, questionnaire_id = found
    answers = session.scalars(select(AnswerRow).where(AnswerRow.questionnaire_id == questionnaire_id)).all()
    steps = session.scalars(
        select(PlanStepRow).where(PlanStepRow.plan_id == plan.id).order_by(PlanStepRow.position)
    ).all()
    return SavedPlan(
        id=plan.id,
        created_at=plan.created_at,
        answers=[(row.question_code, row.answer_code, row.text) for row in answers],
        steps=[PlanStep(step.position, step.step_code, step.done_at) for step in steps],
    )


def set_step_done(session: Session, plan_id: int, position: int, done_at: datetime | None) -> None:
    session.execute(
        update(PlanStepRow)
        .where(PlanStepRow.plan_id == plan_id, PlanStepRow.position == position)
        .values(done_at=done_at)
    )
