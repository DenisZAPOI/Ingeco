"""Responses of /practical-guides (practical guides "Comment faire ?", module M5)."""

from datetime import date

from pydantic import Field

from ..repository.practical_guide_repository import PracticalGuide
from .base import ApiModel
from .help_service_dto import HelpCategory


class GuideSourceDto(ApiModel):
    """The official page that keeps the rules up to date."""

    name: str = Field(examples=["ameli.fr (Assurance maladie)"])
    url: str = Field(examples=["https://www.ameli.fr/"])


class PracticalGuideDto(ApiModel):
    id: int
    # The need of the help directory the guide belongs to.
    category: HelpCategory
    title: str = Field(examples=["S'inscrire à France Travail"])
    intro: str
    # In order: one short sentence each, also read aloud by the phone.
    steps: list[str]
    # What to take along; empty when nothing special is needed.
    to_bring: list[str]
    # null when there is no reliable national page: a step names where to ask.
    source: GuideSourceDto | None
    updated_on: date
    # Language of the texts: the one asked for, or "fr".
    language: str = Field(examples=["fr"])


class PracticalGuideListDto(ApiModel):
    items: list[PracticalGuideDto]


def practical_guide_to_dto(guide: PracticalGuide) -> PracticalGuideDto:
    source = (
        GuideSourceDto(name=guide.source_name, url=guide.source_url)
        if guide.source_name is not None and guide.source_url is not None
        else None
    )
    return PracticalGuideDto(
        id=guide.id,
        category=guide.category,
        title=guide.title,
        intro=guide.intro,
        steps=list(guide.steps),
        to_bring=list(guide.to_bring),
        source=source,
        updated_on=guide.updated_on,
        language=guide.language,
    )
