"""Responses of /jobs (job offers, module M2)."""

from datetime import datetime
from typing import Literal

from pydantic import Field

from ..services import place_service
from ..services.job_service import OfferWithCommune
from .base import ApiModel
from .ride_dto import StopDto

ContractType = Literal["permanent", "fixed_term", "temp", "apprenticeship", "seasonal"]
Schedule = Literal["day", "shifted", "night"]


class JobOfferDto(ApiModel):
    id: int
    title: str = Field(examples=["Employé(e) de rayon"])
    employer: str
    description: str
    contract_type: ContractType
    # Hours of the job: daytime, early or late ("shifted"), or night.
    schedule: Schedule
    part_time: bool
    beginner_welcome: bool
    no_diploma_required: bool
    # Where the job is, signed like a place of GET /places: "Comment y aller ?"
    # books a trip there without asking the address again.
    place: StopDto
    commune_name: str = Field(examples=["Matoury"])
    published_at: datetime
    # Language of title, employer and description: the one asked for, or "fr"
    # when the offer is not translated into it (marked on the page for screen
    # readers).
    language: str = Field(examples=["fr"])


class JobOfferListDto(ApiModel):
    items: list[JobOfferDto]


def job_offer_to_dto(found: OfferWithCommune) -> JobOfferDto:
    offer = found.offer
    return JobOfferDto(
        id=offer.id,
        title=offer.title,
        employer=offer.employer,
        description=offer.description,
        contract_type=offer.contract_type,
        schedule=offer.schedule,
        part_time=offer.part_time,
        beginner_welcome=offer.beginner_welcome,
        no_diploma_required=offer.no_diploma_required,
        place=StopDto(
            address=offer.address,
            lat=offer.lat,
            lng=offer.lng,
            commune_id=offer.commune_id,
            token=place_service.place_token(offer.address, offer.lat, offer.lng, offer.commune_id),
        ),
        commune_name=found.commune_name,
        published_at=offer.published_at,
        language=offer.language,
    )
