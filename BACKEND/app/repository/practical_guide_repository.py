"""
Practical guides "Comment faire ?" (module M5 of the cahier des charges):
tables `fiche_pratique`, `fiche_pratique_traduction`, `fiche_pratique_etape`
and `fiche_pratique_a_apporter` of the DB team (migrations 013 and 016,
issue #49).

Unlike the help services, these guides describe real procedures. They stay
general (no amount, no deadline) and name their official source, where the
rules are kept up to date; the client proofreads them (cahier des charges
§15). No guide asks for nor speaks of nationality or residence status (§12).

A guide is read entirely in one language, never mixed: the translation row
AND the steps of that language, or everything in French. Steps and things to
bring carry their language, French included.
"""

from dataclasses import dataclass
from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from ..models import (
    PracticalGuideItemRow,
    PracticalGuideRow,
    PracticalGuideStepRow,
    PracticalGuideTranslationRow,
)
from .help_service_repository import CATEGORIES, category_from_row

_FRENCH = "fr"


@dataclass(frozen=True)
class PracticalGuide:
    id: int
    category: str
    title: str
    intro: str
    steps: tuple[str, ...]
    # What to take along; empty when nothing special is needed.
    to_bring: tuple[str, ...]
    # The official page that keeps the rules up to date; None when there is
    # no reliable national page (then a step names the local place to ask).
    source_name: str | None
    source_url: str | None
    updated_on: date
    # The language of the texts ("fr" when untranslated).
    language: str = _FRENCH


def list_guides(session: Session, language: str) -> list[PracticalGuide]:
    """Every guide online, in the order of the needs (cahier des charges §7.5)."""
    rows = session.execute(_with_translation(language).where(PracticalGuideRow.is_active.is_(True))).all()
    guides = _to_guides(session, rows, language)
    order = {category: index for index, category in enumerate(CATEGORIES)}
    return sorted(guides, key=lambda guide: (order[guide.category], guide.id))


def find_by_id(session: Session, guide_id: int, language: str) -> PracticalGuide | None:
    query = _with_translation(language).where(
        PracticalGuideRow.id == guide_id, PracticalGuideRow.is_active.is_(True)
    )
    rows = session.execute(query).all()
    guides = _to_guides(session, rows, language)
    return guides[0] if guides else None


def _with_translation(language: str):
    """Each guide with its translation in `language`, or None (LEFT JOIN)."""
    return select(PracticalGuideRow, PracticalGuideTranslationRow).outerjoin(
        PracticalGuideTranslationRow,
        and_(
            PracticalGuideTranslationRow.guide_id == PracticalGuideRow.id,
            PracticalGuideTranslationRow.language == language,
        ),
    )


def _to_guides(session: Session, rows, language: str) -> list[PracticalGuide]:
    """Two queries for the lists of every guide (steps, things to bring), in
    French and in `language`: never one query per guide."""
    guide_ids = [row.id for row, _ in rows]
    languages = {_FRENCH, language}
    steps = _lists(session, PracticalGuideStepRow, guide_ids, languages)
    items = _lists(session, PracticalGuideItemRow, guide_ids, languages)
    guides = []
    for row, text in rows:
        # Translated only when the steps exist in that language too: a
        # translated title over French steps would mix two languages.
        translated = text is not None and (row.id, language) in steps
        used = language if translated else _FRENCH
        source = text if translated else row
        guides.append(
            PracticalGuide(
                id=row.id,
                category=category_from_row(row.category),
                title=source.title,
                intro=source.introduction,
                steps=steps.get((row.id, used), ()),
                to_bring=items.get((row.id, used), ()),
                source_name=source.source_name,
                source_url=row.source_url,
                updated_on=row.updated_on,
                language=used,
            )
        )
    return guides


def _lists(
    session: Session,
    table: type[PracticalGuideStepRow] | type[PracticalGuideItemRow],
    guide_ids: list[int],
    languages: set[str],
) -> dict[tuple[int, str], tuple[str, ...]]:
    """The lines of each guide in each language, in their order."""
    if not guide_ids:
        return {}
    query = (
        select(table.guide_id, table.language, table.text)
        .where(table.guide_id.in_(guide_ids), table.language.in_(languages))
        .order_by(table.guide_id, table.language, table.position)
    )
    lists: dict[tuple[int, str], list[str]] = {}
    for guide_id, code, line in session.execute(query):
        lists.setdefault((guide_id, code), []).append(line)
    return {key: tuple(lines) for key, lines in lists.items()}
