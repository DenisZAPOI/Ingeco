"""
Diagnostic of the API and its database.

A controller turns HTTP into service calls, and results into responses.
No business rule, no SQL here.
"""

from flask import Blueprint, jsonify
from flask_pydantic_spec import Response

from ..dtos.health_dto import HealthDto, degraded_health_dto, health_to_dto
from ..extensions import spec
from ..services import health_service
from ..services.health_service import DatabaseUnreachable

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
@spec.validate(resp=Response(HTTP_200=HealthDto, HTTP_503=HealthDto), tags=["Diagnostic"])
def health():
    """State of the API and its database.

    Switches to 503 when the database is down: a route answering 200 without
    querying the database would prove nothing.
    """
    try:
        state = health_service.database_state()
    except DatabaseUnreachable:
        return jsonify(degraded_health_dto().to_json()), 503
    return jsonify(health_to_dto(state).to_json()), 200
