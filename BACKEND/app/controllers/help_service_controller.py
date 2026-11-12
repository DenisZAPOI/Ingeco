"""Directory of help services (module M5). Public routes: no account needed to read them."""

from flask import Blueprint, jsonify
from flask_pydantic_spec import Response

from ..dtos.base import ErrorDto
from ..dtos.help_service_dto import HelpServiceDto, HelpServiceListDto, help_service_to_dto
from ..extensions import spec
from ..services import help_service_service
from ..utils.language import request_language

help_service_bp = Blueprint("help_services", __name__)

_TAGS = ["Annuaire"]


@help_service_bp.get("/help-services")
@spec.validate(resp=Response(HTTP_200=HelpServiceListDto), tags=_TAGS)
def list_help_services():
    """The help services, by need (same order in every language), in the language of
    Accept-Language where translated (French otherwise: `language` says which).

    All of them at once (a few dozen at most): the phone filters them by need
    and commune itself, without a round trip at each choice.
    """
    services = [help_service_to_dto(found) for found in help_service_service.list_services(request_language())]
    return jsonify(HelpServiceListDto(items=services).to_json()), 200


@help_service_bp.get("/help-services/<int:service_id>")
@spec.validate(resp=Response(HTTP_200=HelpServiceDto, HTTP_404=ErrorDto), tags=_TAGS)
def get_help_service(service_id: int):
    """One help service. 404 if it does not exist."""
    found = help_service_service.get_service(service_id, request_language())
    return jsonify(help_service_to_dto(found).to_json()), 200
