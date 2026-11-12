"""Orientation (module M1): questionnaire, reponse_questionnaire, plan_action,
etape_plan (migration 017).

The questions and the rules of the plan live in the API code; the database
keeps only CODES ('sans_emploi', 'besoin_garde'…), never labels, and never a
forbidden field (cahier des charges §12): a need is written as a need, never
as a diagnosis. No automatic decision (GDPR art. 22): a person can take the
plan over, `updated_at` and `updated_by_id` say who and when.
"""

from datetime import datetime

from sqlalchemy import ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from ..utils.database import Base
from .types import UtcDateTime


class QuestionnaireRow(Base):
    """One filling of the questionnaire; the most recent one counts."""

    __tablename__ = "questionnaire"

    id: Mapped[int] = mapped_column("id_questionnaire", Integer, primary_key=True)
    rider_id: Mapped[int] = mapped_column("id_usager", Integer, ForeignKey("usager.id_utilisateur"))
    filled_at: Mapped[datetime] = mapped_column("rempli_le", UtcDateTime)


class AnswerRow(Base):
    """One answer; a multiple-choice question has one row per ticked choice."""

    __tablename__ = "reponse_questionnaire"

    questionnaire_id: Mapped[int] = mapped_column(
        "id_questionnaire", Integer, ForeignKey("questionnaire.id_questionnaire"), primary_key=True
    )
    question_code: Mapped[str] = mapped_column("code_question", String(50), primary_key=True)
    answer_code: Mapped[str] = mapped_column("code_reponse", String(50), primary_key=True)
    # Free answer only (informal experiences): erased when the account is deleted
    text: Mapped[str | None] = mapped_column("texte", String(500))


class ActionPlanRow(Base):
    """The plan computed from one questionnaire (one plan per questionnaire)."""

    __tablename__ = "plan_action"

    id: Mapped[int] = mapped_column("id_plan", Integer, primary_key=True)
    questionnaire_id: Mapped[int] = mapped_column(
        "id_questionnaire", Integer, ForeignKey("questionnaire.id_questionnaire"), unique=True
    )
    created_at: Mapped[datetime] = mapped_column("cree_le", UtcDateTime)
    # Last change by a person; both NULL until someone takes the plan over
    updated_at: Mapped[datetime | None] = mapped_column("modifie_le", UtcDateTime)
    updated_by_id: Mapped[int | None] = mapped_column(
        "id_modifie_par", Integer, ForeignKey("utilisateur.id_utilisateur")
    )


class PlanStepRow(Base):
    """Step 1 to 5 of a plan (at least 3: rule of the API). It suggests a help
    service, a job offer, or nothing, never both."""

    __tablename__ = "etape_plan"

    plan_id: Mapped[int] = mapped_column("id_plan", Integer, ForeignKey("plan_action.id_plan"), primary_key=True)
    position: Mapped[int] = mapped_column("ordre", SmallInteger, primary_key=True)
    step_code: Mapped[str] = mapped_column("code_etape", String(50))
    help_service_id: Mapped[int | None] = mapped_column(
        "id_service", Integer, ForeignKey("service_aide.id_service")
    )
    job_offer_id: Mapped[int | None] = mapped_column("id_offre", Integer, ForeignKey("offre_emploi.id_offre"))
    # Ticked by the rider; NULL until done
    done_at: Mapped[datetime | None] = mapped_column("faite_le", UtcDateTime)
