"""
Job offers (module M2): the list and one offer.

Public: anyone may read them, without an account (fictitious offers, no
personal data). Booking a trip to an offer needs an account, like any booking.
"""

from dataclasses import dataclass

from ..repository import commune_repository, job_repository
from ..repository.job_repository import JobOffer
from ..utils import database
from ..utils.errors import NotFound

OFFER_NOT_FOUND = "Cette offre n'existe pas ou n'est plus en ligne."


@dataclass(frozen=True)
class OfferWithCommune:
    offer: JobOffer
    commune_name: str


def list_offers(language: str) -> list[OfferWithCommune]:
    with database.session() as session:
        names = {commune.id: commune.name for commune in commune_repository.list_communes(session, served_only=False)}
        return [_with_commune(offer, names) for offer in job_repository.list_active(session, language)]


def get_offer(offer_id: int, language: str) -> OfferWithCommune:
    with database.session() as session:
        offer = job_repository.find_active(session, offer_id, language)
        if offer is None:
            raise NotFound(OFFER_NOT_FOUND)
        commune = commune_repository.find_by_id(session, offer.commune_id)
        return OfferWithCommune(offer, commune.name if commune else "")


def _with_commune(offer: JobOffer, names: dict[int, str]) -> OfferWithCommune:
    # An offer always points to a row of `commune` (foreign key once in base).
    return OfferWithCommune(offer, names.get(offer.commune_id, ""))
