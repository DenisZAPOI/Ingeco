"""Settings of the administrator (M9, P1): service hours, zones, tariff. Administrators only.

Each change applies to new requests only: rides already booked keep their
time, communes and price.
"""

from flask import Blueprint, jsonify, request
from flask_pydantic_spec import Response

from ..dtos.base import ErrorDto
from ..dtos.settings_dto import (
    TariffBody,
    TariffDto,
    WeekBody,
    WeekDto,
    ZoneListDto,
    ZonesBody,
    tariff_to_dto,
    week_to_dto,
    zones_to_dto,
)
from ..extensions import spec
from ..services import settings_service
from ..utils.access import current_user_id, require_login

settings_bp = Blueprint("settings", __name__, url_prefix="/admin")

_TAGS = ["Réglages"]
_ADMIN = "admin"


@settings_bp.get("/service-hours")
@require_login(_ADMIN)
@spec.validate(resp=Response(HTTP_200=WeekDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto), tags=_TAGS)
def get_service_hours():
    """The hours when a ride can be requested, day by day, in local time of Cayenne."""
    days = settings_service.get_week()
    return jsonify(week_to_dto(days).to_json()), 200


@settings_bp.put("/service-hours")
@require_login(_ADMIN)
@spec.validate(
    body=WeekBody,
    resp=Response(HTTP_200=WeekDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_422=ErrorDto),
    tags=_TAGS,
)
def put_service_hours():
    """Replaces the hours of the whole week: one slot per day, or closed.

    422 if every day is closed.
    """
    body: WeekBody = request.context.body
    days = settings_service.save_week(admin_id=current_user_id(), days=body.to_days())
    return jsonify(week_to_dto(days).to_json()), 200


@settings_bp.get("/zones")
@require_login(_ADMIN)
@spec.validate(resp=Response(HTTP_200=ZoneListDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto), tags=_TAGS)
def get_zones():
    """The 22 communes of French Guiana, and which ones receive rides."""
    communes = settings_service.list_zones()
    return jsonify(zones_to_dto(communes).to_json()), 200


@settings_bp.put("/zones")
@require_login(_ADMIN)
@spec.validate(
    body=ZonesBody,
    resp=Response(HTTP_200=ZoneListDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_422=ErrorDto),
    tags=_TAGS,
)
def put_zones():
    """The communes that receive rides from now on; every other one stops.

    422 if none is left, or one does not exist.
    """
    body: ZonesBody = request.context.body
    communes = settings_service.save_zones(admin_id=current_user_id(), served_ids=set(body.served_commune_ids))
    return jsonify(zones_to_dto(communes).to_json()), 200


@settings_bp.get("/tariff")
@require_login(_ADMIN)
@spec.validate(resp=Response(HTTP_200=TariffDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto), tags=_TAGS)
def get_tariff():
    """The tariff of the next bookings."""
    tariff = settings_service.get_tariff()
    return jsonify(tariff_to_dto(tariff).to_json()), 200


@settings_bp.post("/tariff")
@require_login(_ADMIN)
@spec.validate(
    body=TariffBody,
    resp=Response(HTTP_201=TariffDto, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto),
    tags=_TAGS,
)
def post_tariff():
    """A new version of the tariff, for the next bookings. The old one is kept for the rides booked with it."""
    body: TariffBody = request.context.body
    tariff = settings_service.new_tariff(
        admin_id=current_user_id(),
        base_fare_cents=body.base_fare_cents,
        per_km_cents=body.per_km_cents,
    )
    return jsonify(tariff_to_dto(tariff).to_json()), 201
