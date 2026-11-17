"""
Job offers (module M2 of the cahier des charges): tables `offre_emploi` and
`offre_emploi_traduction` of the DB team (migrations 011 and 014, issue #48).

Every offer is fictitious (cahier des charges §5: no real data): the rows are
written by migration 014 and stay when the demo is reset.

Texts are in French in `offre_emploi`, and in the other languages in
`offre_emploi_traduction` where we have a translation (ADR 018). An offer is
read in one language: the three texts come from the same row, French when the
language has none, and the offer says which language it is in.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from ..models import JobOfferRow, JobOfferTranslationRow

# Values of the filters, in English for the API; the ENUM of the table is in French.
CONTRACT_TYPES = ("permanent", "fixed_term", "temp", "apprenticeship", "seasonal")
SCHEDULES = ("day", "shifted", "night")

_CONTRACT_FROM_ROW = dict(zip(("cdi", "cdd", "interim", "alternance", "saisonnier"), CONTRACT_TYPES))
_SCHEDULE_FROM_ROW = dict(zip(("journee", "horaires_decales", "nuit"), SCHEDULES))
_FRENCH = "fr"


@dataclass(frozen=True)
class JobOffer:
    id: int
    title: str
    employer: str
    description: str
    contract_type: str
    schedule: str
    part_time: bool
    beginner_welcome: bool
    no_diploma_required: bool
    address: str
    lat: float
    lng: float
    commune_id: int
    published_at: datetime
    active: bool = True
    # The language of title, employer and description ("fr" when untranslated).
    language: str = _FRENCH


def list_active(session: Session, language: str) -> list[JobOffer]:
    """The offers online, the most recent first, in `language` where translated.

    Served by idx_offre_emploi_liste (active, id_commune, publiee_le)."""
    query = (
        _with_translation(language)
        .where(JobOfferRow.is_active.is_(True))
        .order_by(JobOfferRow.published_at.desc(), JobOfferRow.id.desc())
    )
    return [_to_offer(row, text) for row, text in session.execute(query)]


def find_active(session: Session, offer_id: int, language: str) -> JobOffer | None:
    query = _with_translation(language).where(JobOfferRow.id == offer_id, JobOfferRow.is_active.is_(True))
    found = session.execute(query).first()
    return _to_offer(*found) if found else None


def _with_translation(language: str):
    """Each offer with its translation in `language`, or None (LEFT JOIN)."""
    return select(JobOfferRow, JobOfferTranslationRow).outerjoin(
        JobOfferTranslationRow,
        and_(JobOfferTranslationRow.offer_id == JobOfferRow.id, JobOfferTranslationRow.language == language),
    )


def _to_offer(row: JobOfferRow, text: JobOfferTranslationRow | None) -> JobOffer:
    """All three texts in the same language: never a title in English over a
    description in French."""
    source = text or row
    return JobOffer(
        id=row.id,
        title=source.title,
        employer=source.employer,
        description=source.description,
        contract_type=_CONTRACT_FROM_ROW[row.contract_type],
        schedule=_SCHEDULE_FROM_ROW[row.schedule],
        part_time=row.part_time,
        beginner_welcome=row.beginner_welcome,
        no_diploma_required=row.no_diploma,
        address=row.address,
        lat=float(row.lat),
        lng=float(row.lng),
        commune_id=row.commune_id,
        published_at=row.published_at,
        active=row.is_active,
        language=text.language if text else _FRENCH,
    )
