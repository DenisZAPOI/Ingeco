"""Job offers (module M2). Public routes: no account needed to read them."""

from flask import Blueprint, jsonify
from flask_pydantic_spec import Response

from ..dtos.base import ErrorDto
from ..dtos.job_dto import JobOfferDto, JobOfferListDto, job_offer_to_dto
from ..extensions import spec
from ..services import job_service
from ..utils.language import request_language

job_bp = Blueprint("jobs", __name__)

_TAGS = ["Emploi"]


@job_bp.get("/jobs")
@spec.validate(resp=Response(HTTP_200=JobOfferListDto), tags=_TAGS)
def list_jobs():
    """The job offers online, the most recent first, in the language of
    Accept-Language where translated (French otherwise: `language` says which).

    All of them at once (a few dozen at most): the phone filters them itself,
    without a round trip at each filter.
    """
    offers = [job_offer_to_dto(found) for found in job_service.list_offers(request_language())]
    return jsonify(JobOfferListDto(items=offers).to_json()), 200


@job_bp.get("/jobs/<int:offer_id>")
@spec.validate(resp=Response(HTTP_200=JobOfferDto, HTTP_404=ErrorDto), tags=_TAGS)
def get_job(offer_id: int):
    """One offer. 404 if it does not exist or is no longer online."""
    return jsonify(job_offer_to_dto(job_service.get_offer(offer_id, request_language())).to_json()), 200
