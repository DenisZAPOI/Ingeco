"""
Help services of the directory (module M5 of the cahier des charges): tables
`service_aide`, `service_aide_langue` and `service_aide_traduction` of the DB
team (migrations 012 and 015, issue #49).

Every service is fictitious (cahier des charges §5: no real data): invented
names marked "(fictif)", placed at public places of the pilot zone. Their
phone numbers are in the range the ARCEP reserves for fiction (05 36 49 xx xx):
they ring at nobody's. A health service describes a place to go, never an
illness (§12). The rows are written by migration 015 and stay when the demo is
reset; a closed service has `actif` = FALSE and is not listed.

Texts are in French in `service_aide`, translated in `service_aide_traduction`
where we have a translation (ADR 018), the same way as the job offers.
"""

from dataclasses import dataclass
from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from ..models import HelpServiceLanguageRow, HelpServiceRow, HelpServiceTranslationRow

# The needs of the directory, in the order of the cahier des charges (§7.5),
# in English for the API; the ENUM `categorie` of the table is in French.
CATEGORIES = ("childcare", "housing", "rights", "health", "food", "digital", "paperwork", "equipment")
_CATEGORY_FROM_ROW = dict(
    zip(
        ("garde", "logement", "droits", "sante", "aide_alimentaire", "numerique", "demarches", "equipement"),
        CATEGORIES,
    )
)
_CATEGORY_TO_ROW = {category: row for row, category in _CATEGORY_FROM_ROW.items()}

# Spoken languages are listed in the order of the language picker of the
# interface, whatever the order of the rows.
_LANGUAGE_ORDER = ("fr", "gcr", "ht", "pt-BR", "en")
_FRENCH = "fr"


@dataclass(frozen=True)
class HelpService:
    id: int
    name: str
    category: str
    description: str
    hours: str
    address: str
    lat: float
    lng: float
    commune_id: int
    # International format; a fictitious number of the ARCEP range.
    phone: str | None
    wheelchair_accessible: bool
    spoken_languages: tuple[str, ...]
    updated_on: date
    # The language of name, description and hours ("fr" when untranslated).
    language: str = _FRENCH


def category_to_row(category: str) -> str:
    """The French ENUM value of a need, for the other tables that use the same list."""
    return _CATEGORY_TO_ROW[category]


def category_from_row(value: str) -> str:
    return _CATEGORY_FROM_ROW[value]


def list_services(session: Session, language: str) -> list[HelpService]:
    """Every open service, by need, in `language` where translated. Same order
    in every language: the list does not move when the phone changes language."""
    rows = session.execute(_with_translation(language).where(HelpServiceRow.is_active.is_(True))).all()
    spoken = _spoken_languages(session, [row.id for row, _ in rows])
    order = {category: index for index, category in enumerate(CATEGORIES)}
    services = [_to_service(row, text, spoken.get(row.id, ())) for row, text in rows]
    return sorted(services, key=lambda service: (order[service.category], service.id))


def find_by_id(session: Session, service_id: int, language: str) -> HelpService | None:
    query = _with_translation(language).where(HelpServiceRow.id == service_id, HelpServiceRow.is_active.is_(True))
    found = session.execute(query).first()
    if found is None:
        return None
    row, text = found
    return _to_service(row, text, _spoken_languages(session, [row.id]).get(row.id, ()))


def _with_translation(language: str):
    """Each service with its translation in `language`, or None (LEFT JOIN)."""
    return select(HelpServiceRow, HelpServiceTranslationRow).outerjoin(
        HelpServiceTranslationRow,
        and_(
            HelpServiceTranslationRow.service_id == HelpServiceRow.id,
            HelpServiceTranslationRow.language == language,
        ),
    )


def _spoken_languages(session: Session, service_ids: list[int]) -> dict[int, tuple[str, ...]]:
    """One query for every service of the list, not one per service."""
    if not service_ids:
        return {}
    rows = session.execute(
        select(HelpServiceLanguageRow.service_id, HelpServiceLanguageRow.language).where(
            HelpServiceLanguageRow.service_id.in_(service_ids)
        )
    )
    by_service: dict[int, list[str]] = {}
    for service_id, code in rows:
        by_service.setdefault(service_id, []).append(code)
    rank = {code: index for index, code in enumerate(_LANGUAGE_ORDER)}
    return {
        service_id: tuple(sorted(codes, key=lambda code: rank.get(code, len(rank))))
        for service_id, codes in by_service.items()
    }


def _to_service(row: HelpServiceRow, text: HelpServiceTranslationRow | None, spoken: tuple[str, ...]) -> HelpService:
    """Name, description and hours in the same language, never a mix."""
    source = text or row
    return HelpService(
        id=row.id,
        name=source.name,
        category=_CATEGORY_FROM_ROW[row.category],
        description=source.description,
        hours=source.opening_hours,
        address=row.address,
        lat=float(row.lat),
        lng=float(row.lng),
        commune_id=row.commune_id,
        phone=row.phone,
        wheelchair_accessible=row.wheelchair_accessible,
        spoken_languages=spoken,
        updated_on=row.updated_on,
        language=text.language if text else _FRENCH,
    )
