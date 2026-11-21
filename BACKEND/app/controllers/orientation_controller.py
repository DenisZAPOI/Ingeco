"""Orientation questionnaire and action plan (module M1)."""

from flask import Blueprint, jsonify, request
from flask_pydantic_spec import Response

from ..dtos.base import ErrorDto
from ..dtos.orientation_dto import (
    AnswersDto,
    PlanDto,
    PlanPreviewDto,
    StepDoneBody,
    plan_to_dto,
    preview_to_dto,
)
from ..extensions import spec
from ..services import orientation_service
from ..utils.access import current_user_id, require_login

orientation_bp = Blueprint("orientation", __name__, url_prefix="/orientation")

_TAGS = ["Orientation"]


@orientation_bp.post("/plan")
@spec.validate(body=AnswersDto, resp=Response(HTTP_200=PlanPreviewDto, HTTP_400=ErrorDto), tags=_TAGS)
def preview_plan():
    """The action plan for these answers, for anyone, without an account. Keeps nothing.

    400 if an answer is unknown, or if "nothing of all that" is ticked with
    another answer.
    """
    body: AnswersDto = request.context.body
    steps = orientation_service.preview(body.to_answers())
    return jsonify(preview_to_dto(steps).to_json()), 200


@orientation_bp.post("/questionnaires")
@require_login("rider")
@spec.validate(
    body=AnswersDto,
    resp=Response(HTTP_201=PlanDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto),
    tags=_TAGS,
)
def save_questionnaire():
    """Keeps the rider's answers and their plan, which becomes the current plan.

    Answering again keeps the earlier fillings; the most recent one counts.
    """
    body: AnswersDto = request.context.body
    plan = orientation_service.save(current_user_id(), body.to_answers())
    return jsonify(plan_to_dto(plan).to_json()), 201


@orientation_bp.get("/plan")
@require_login("rider")
@spec.validate(resp=Response(HTTP_200=PlanDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto), tags=_TAGS)
def current_plan():
    """The rider's current plan and the answers it comes from. 404 before any questionnaire."""
    plan = orientation_service.current(current_user_id())
    return jsonify(plan_to_dto(plan).to_json()), 200


@orientation_bp.put("/plan/steps/<int:position>")
@require_login("rider")
@spec.validate(
    body=StepDoneBody,
    resp=Response(HTTP_200=PlanDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto),
    tags=_TAGS,
)
def mark_plan_step(position: int):
    """« C'est fait » on a step of the current plan, or taken back. Sent twice, same result.

    404 if the rider has no plan, or no step at this position.
    """
    body: StepDoneBody = request.context.body
    plan = orientation_service.mark_step(current_user_id(), position, body.done)
    return jsonify(plan_to_dto(plan).to_json()), 200
