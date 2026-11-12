"""Responses of /help-services (directory of help services, module M5)."""

from datetime import date
from typing import Literal

from pydantic import Field

from ..services import place_service
from ..services.help_service_service import ServiceWithCommune
from .base import ApiModel
from .ride_dto import StopDto

HelpCategory = Literal["childcare", "housing", "rights", "health", "food", "digital", "paperwork", "equipment"]
SpokenLanguage = Literal["fr", "gcr", "ht", "pt-BR", "en"]


class HelpServiceDto(ApiModel):
    id: int
    name: str = Field(examples=["Point info logement (fictif)"])
    category: HelpCategory
    description: str
    # Opening hours, as written by the service ("Du lundi au vendredi, 8 h – 12 h").
    hours: str
    # Where the service is, signed like a place of GET /places: "Comment y
    # aller ?" books a trip there without asking the address again.
    place: StopDto
    commune_name: str = Field(examples=["Cayenne"])
    # International format. Fictitious numbers of the range the ARCEP reserves for fiction.
    phone: str = Field(examples=["+33536490003"])
    wheelchair_accessible: bool
    spoken_languages: list[SpokenLanguage]
    updated_on: date
    # Language of name, description and hours: the one asked for, or "fr".
    language: str = Field(examples=["fr"])


class HelpServiceListDto(ApiModel):
    items: list[HelpServiceDto]


def help_service_to_dto(found: ServiceWithCommune) -> HelpServiceDto:
    service = found.service
    return HelpServiceDto(
        id=service.id,
        name=service.name,
        category=service.category,
        description=service.description,
        hours=service.hours,
        place=StopDto(
            address=service.address,
            lat=service.lat,
            lng=service.lng,
            commune_id=service.commune_id,
            token=place_service.place_token(service.address, service.lat, service.lng, service.commune_id),
        ),
        commune_name=found.commune_name,
        phone=service.phone,
        wheelchair_accessible=service.wheelchair_accessible,
        spoken_languages=list(service.spoken_languages),
        updated_on=service.updated_on,
        language=service.language,
    )
