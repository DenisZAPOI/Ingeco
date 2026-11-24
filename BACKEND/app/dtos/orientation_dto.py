"""Requests and responses of /orientation (questionnaire and action plan, module M1)."""

from datetime import datetime

from pydantic import Field, field_validator

from ..repository.orientation_repository import SavedPlan
from ..services import orientation_rules as rules
from ..services.orientation_rules import (
    Answers,
    Availability,
    DigitalEquipment,
    FrenchLevel,
    Experience,
    Need,
    Project,
    Situation,
    StepCode,
)
from .base import ApiModel, InputModel, apply_rule


class AnswersDto(InputModel):
    """The answers to the 7 questions. Every question may be skipped: null or []."""

    situation: Situation | None = None
    project: Project | None = None
    experiences: list[Experience] = Field(default_factory=list, examples=[["agriculture", "benevolat"]])
    # Informal experiences in the person's words. Never health nor papers (§12):
    # the screen says so.
    experience_text: str | None = Field(
        None, max_length=rules.EXPERIENCE_TEXT_MAX_LENGTH, examples=["J'aide mon oncle à l'abattis le week-end"]
    )
    availability: list[Availability] = Field(default_factory=list, examples=[["matin", "apres_midi"]])
    needs: list[Need] = Field(default_factory=list, examples=[["trajet"]])
    # "Êtes-vous à l'aise en français ?" (never the languages spoken: audit RGPD R6)
    french: FrenchLevel | None = Field(None, examples=["oui"])
    digital_equipment: list[DigitalEquipment] = Field(default_factory=list, examples=[["smartphone"]])

    @field_validator("experience_text")
    @classmethod
    def _blank_is_none(cls, text: str | None) -> str | None:
        return text.strip() or None if text is not None else None

    @field_validator("experiences")
    @classmethod
    def _no_experience_alone(cls, chosen: list[str]) -> list[str]:
        return apply_rule(lambda value: rules.check_alone(value, rules.NO_EXPERIENCE), chosen)

    @field_validator("needs")
    @classmethod
    def _no_need_alone(cls, chosen: list[str]) -> list[str]:
        return apply_rule(lambda value: rules.check_alone(value, rules.NO_NEED), chosen)

    @field_validator("digital_equipment")
    @classmethod
    def _no_equipment_alone(cls, chosen: list[str]) -> list[str]:
        return apply_rule(lambda value: rules.check_alone(value, rules.NO_EQUIPMENT), chosen)

    @field_validator("availability")
    @classmethod
    def _no_duplicate(cls, chosen: list[str]) -> list[str]:
        return list(dict.fromkeys(chosen))

    def to_answers(self) -> Answers:
        return Answers(
            situation=self.situation,
            project=self.project,
            experiences=tuple(self.experiences),
            experience_text=self.experience_text,
            availability=tuple(self.availability),
            needs=tuple(self.needs),
            french=self.french,
            digital_equipment=tuple(self.digital_equipment),
        )


class StepDoneBody(InputModel):
    done: bool


class PlanStepDto(ApiModel):
    position: int = Field(ge=1, le=rules.MAX_STEPS, examples=[1])
    # The front-end shows its title, text and button in the user's language.
    code: StepCode
    # When the rider ticked it; always null for a plan not kept.
    done_at: datetime | None


class PlanPreviewDto(ApiModel):
    """A plan computed without an account: nothing is kept."""

    steps: list[PlanStepDto]


class PlanDto(ApiModel):
    """The rider's current plan, with the answers it comes from ("Modifier mes réponses")."""

    created_at: datetime
    steps: list[PlanStepDto]
    answers: AnswersDto


def preview_to_dto(steps: list[str]) -> PlanPreviewDto:
    return PlanPreviewDto(
        steps=[PlanStepDto(position=index, code=code, done_at=None) for index, code in enumerate(steps, 1)]  # type: ignore[arg-type]
    )


def plan_to_dto(plan: SavedPlan) -> PlanDto:
    answers = rules.from_rows(plan.answers)
    return PlanDto(
        created_at=plan.created_at,
        steps=[PlanStepDto(position=step.position, code=step.code, done_at=step.done_at) for step in plan.steps],  # type: ignore[arg-type]
        answers=AnswersDto.model_validate(
            {
                "situation": answers.situation,
                "project": answers.project,
                "experiences": list(answers.experiences),
                "experience_text": answers.experience_text,
                "availability": list(answers.availability),
                "needs": list(answers.needs),
                "french": answers.french,
                "digital_equipment": list(answers.digital_equipment),
            }
        ),
    )
