"""
Practical guides "Comment faire ?" (module M5): the list and one guide.

Public: anyone may read them, without an account (general guides, no
personal data).
"""

from ..repository import practical_guide_repository
from ..repository.practical_guide_repository import PracticalGuide
from ..utils import database
from ..utils.errors import NotFound

GUIDE_NOT_FOUND = "Cette fiche n'existe pas."


def list_guides(language: str) -> list[PracticalGuide]:
    with database.session() as session:
        return practical_guide_repository.list_guides(session, language)


def get_guide(guide_id: int, language: str) -> PracticalGuide:
    with database.session() as session:
        guide = practical_guide_repository.find_by_id(session, guide_id, language)
        if guide is None:
            raise NotFound(GUIDE_NOT_FOUND)
        return guide
