"""Practical guides "Comment faire ?" (module M5). Public routes: no account needed."""

from flask import Blueprint, jsonify
from flask_pydantic_spec import Response

from ..dtos.base import ErrorDto
from ..dtos.practical_guide_dto import PracticalGuideDto, PracticalGuideListDto, practical_guide_to_dto
from ..extensions import spec
from ..services import practical_guide_service
from ..utils.language import request_language

practical_guide_bp = Blueprint("practical_guides", __name__)

_TAGS = ["Annuaire"]


@practical_guide_bp.get("/practical-guides")
@spec.validate(resp=Response(HTTP_200=PracticalGuideListDto), tags=_TAGS)
def list_practical_guides():
    """Every guide, in the order of the needs, in the language of
    Accept-Language where translated (French otherwise: `language` says which).

    All of them at once (a handful): the phone keeps them and filters by need.
    """
    guides = [practical_guide_to_dto(guide) for guide in practical_guide_service.list_guides(request_language())]
    return jsonify(PracticalGuideListDto(items=guides).to_json()), 200


@practical_guide_bp.get("/practical-guides/<int:guide_id>")
@spec.validate(resp=Response(HTTP_200=PracticalGuideDto, HTTP_404=ErrorDto), tags=_TAGS)
def get_practical_guide(guide_id: int):
    """One guide. 404 if it does not exist."""
    guide = practical_guide_service.get_guide(guide_id, request_language())
    return jsonify(practical_guide_to_dto(guide).to_json()), 200
