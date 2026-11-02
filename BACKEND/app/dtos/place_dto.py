"""Responses and query of /communes and /places."""

from pydantic import Field, field_validator

from ..repository.commune_repository import Commune
from ..repository.place_repository import Place
from ..services import place_service
from ..services.account_rules import clean_name
from .base import ApiModel, InputModel, apply_rule, field_error

SEARCH_MIN_LENGTH = 2
SEARCH_MAX_LENGTH = 100


class CommuneDto(ApiModel):
    id: int
    name: str = Field(examples=["Cayenne"])


class CommuneListDto(ApiModel):
    items: list[CommuneDto]


class PlaceQuery(InputModel):
    search: str = Field(max_length=SEARCH_MAX_LENGTH, examples=["mairie"])
    commune_id: int = Field(ge=1)

    @field_validator("search")
    @classmethod
    def _search(cls, value: str) -> str:
        text = apply_rule(clean_name, value)
        if len(text) < SEARCH_MIN_LENGTH:
            raise field_error(f"Tapez au moins {SEARCH_MIN_LENGTH} lettres.")
        return text


class PlaceDto(ApiModel):
    label: str = Field(examples=["Mairie de Matoury"])
    lat: float
    lng: float
    commune_id: int
    # Sent back as is with the stop of an estimate or a booking (StopBody.token).
    token: str


class PlaceListDto(ApiModel):
    items: list[PlaceDto]


def commune_to_dto(commune: Commune) -> CommuneDto:
    return CommuneDto(id=commune.id, name=commune.name)


def place_to_dto(place: Place) -> PlaceDto:
    return PlaceDto(
        label=place.label,
        lat=place.lat,
        lng=place.lng,
        commune_id=place.commune_id,
        token=place_service.place_token(place.label, place.lat, place.lng, place.commune_id),
    )
