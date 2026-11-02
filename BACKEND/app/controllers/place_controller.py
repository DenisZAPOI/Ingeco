"""The served zone: communes and address search."""

from flask import Blueprint, jsonify, request
from flask_pydantic_spec import Response

from ..dtos.base import ErrorDto
from ..dtos.place_dto import CommuneListDto, PlaceListDto, PlaceQuery, commune_to_dto, place_to_dto
from ..extensions import spec
from ..services import place_service
from ..utils.access import require_login

place_bp = Blueprint("places", __name__)

_TAGS = ["Réservation"]


@place_bp.get("/communes")
@require_login()
@spec.validate(resp=Response(HTTP_200=CommuneListDto, HTTP_401=ErrorDto), tags=_TAGS)
def list_communes():
    """The served communes (pilot zone)."""
    communes = [commune_to_dto(commune) for commune in place_service.list_communes()]
    return jsonify(CommuneListDto(items=communes).to_json()), 200


@place_bp.get("/places")
@require_login()
@spec.validate(
    query=PlaceQuery,
    resp=Response(HTTP_200=PlaceListDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_422=ErrorDto, HTTP_503=ErrorDto),
    tags=_TAGS,
)
def search_places():
    """Addresses of a served commune matching the text typed, with their position."""
    query: PlaceQuery = request.context.query
    places = [place_to_dto(place) for place in place_service.search_places(query.search, query.commune_id)]
    return jsonify(PlaceListDto(items=places).to_json()), 200
