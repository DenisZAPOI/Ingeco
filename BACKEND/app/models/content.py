"""Translated contents of the demonstrator: langue, offre_emploi, service_aide,
fiche_pratique and their translations (migrations 009, 011, 012, 013).

French is the reference language: its texts are in the main table, never
empty. The *_traduction tables hold the other languages only; the API falls
back on French when a language has no row. The rows themselves are fictitious
contents written by migrations 014 to 016: they stay when the demo is reset.

An offer, a service or a guide is withdrawn by setting `is_active` to False,
never deleted.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, Boolean, Date, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..utils.database import Base
from .types import UtcDateTime


class LanguageRow(Base):
    """The five languages of the interface, same codes as FRONTEND/src/i18n."""

    __tablename__ = "langue"

    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    label: Mapped[str] = mapped_column("libelle", String(50))


class JobOfferRow(Base):
    """A fictitious job offer. ENUM values in French: 'cdi', 'horaires_decales'…"""

    __tablename__ = "offre_emploi"

    id: Mapped[int] = mapped_column("id_offre", Integer, primary_key=True)
    title: Mapped[str] = mapped_column("intitule", String(150))
    employer: Mapped[str] = mapped_column("employeur", String(150))
    description: Mapped[str] = mapped_column(Text)
    contract_type: Mapped[str] = mapped_column("type_contrat", String(20))
    schedule: Mapped[str] = mapped_column("plage_horaire", String(20))
    part_time: Mapped[bool] = mapped_column("temps_partiel", Boolean)
    beginner_welcome: Mapped[bool] = mapped_column("debutant_accepte", Boolean)
    no_diploma: Mapped[bool] = mapped_column("sans_diplome", Boolean)
    # Workplace, same formats as the arrival of a ride ("Comment y aller ?")
    address: Mapped[str] = mapped_column("adresse", String(255))
    lat: Mapped[Decimal] = mapped_column(DECIMAL(9, 6))
    lng: Mapped[Decimal] = mapped_column(DECIMAL(9, 6))
    commune_id: Mapped[int] = mapped_column("id_commune", Integer, ForeignKey("commune.id_commune"))
    published_at: Mapped[datetime] = mapped_column("publiee_le", UtcDateTime)
    is_active: Mapped[bool] = mapped_column("active", Boolean, default=True)


class JobOfferTranslationRow(Base):
    """The three texts of an offer in one language other than French."""

    __tablename__ = "offre_emploi_traduction"

    offer_id: Mapped[int] = mapped_column(
        "id_offre", Integer, ForeignKey("offre_emploi.id_offre"), primary_key=True
    )
    language: Mapped[str] = mapped_column("code_langue", String(10), ForeignKey("langue.code"), primary_key=True)
    title: Mapped[str] = mapped_column("intitule", String(150))
    employer: Mapped[str] = mapped_column("employeur", String(150))
    description: Mapped[str] = mapped_column(Text)


class HelpServiceRow(Base):
    """A fictitious help service. `category`: one of the eight needs, in French
    ('garde', 'aide_alimentaire'…). A health service describes a place, never
    a condition."""

    __tablename__ = "service_aide"

    id: Mapped[int] = mapped_column("id_service", Integer, primary_key=True)
    name: Mapped[str] = mapped_column("nom", String(150))
    category: Mapped[str] = mapped_column("categorie", String(20))
    description: Mapped[str] = mapped_column(Text)
    # Free text, in Guyana time
    opening_hours: Mapped[str] = mapped_column("horaires", String(255))
    address: Mapped[str] = mapped_column("adresse", String(255))
    lat: Mapped[Decimal] = mapped_column(DECIMAL(9, 6))
    lng: Mapped[Decimal] = mapped_column(DECIMAL(9, 6))
    commune_id: Mapped[int] = mapped_column("id_commune", Integer, ForeignKey("commune.id_commune"))
    phone: Mapped[str | None] = mapped_column("telephone", String(16))
    wheelchair_accessible: Mapped[bool] = mapped_column("accessible_pmr", Boolean)
    updated_on: Mapped[date] = mapped_column("mis_a_jour_le", Date)
    is_active: Mapped[bool] = mapped_column("actif", Boolean, default=True)


class HelpServiceLanguageRow(Base):
    """A language spoken at the service (several per service)."""

    __tablename__ = "service_aide_langue"

    service_id: Mapped[int] = mapped_column(
        "id_service", Integer, ForeignKey("service_aide.id_service"), primary_key=True
    )
    language: Mapped[str] = mapped_column("code_langue", String(10), ForeignKey("langue.code"), primary_key=True)


class HelpServiceTranslationRow(Base):
    __tablename__ = "service_aide_traduction"

    service_id: Mapped[int] = mapped_column(
        "id_service", Integer, ForeignKey("service_aide.id_service"), primary_key=True
    )
    language: Mapped[str] = mapped_column("code_langue", String(10), ForeignKey("langue.code"), primary_key=True)
    name: Mapped[str] = mapped_column("nom", String(150))
    description: Mapped[str] = mapped_column(Text)
    opening_hours: Mapped[str] = mapped_column("horaires", String(255))


class PracticalGuideRow(Base):
    """A "Comment faire ?" guide. Its source is both name and https URL, or
    neither (then a step names the place to ask)."""

    __tablename__ = "fiche_pratique"

    id: Mapped[int] = mapped_column("id_fiche", Integer, primary_key=True)
    category: Mapped[str] = mapped_column("categorie", String(20))
    title: Mapped[str] = mapped_column("titre", String(150))
    introduction: Mapped[str] = mapped_column(String(500))
    source_name: Mapped[str | None] = mapped_column("source_nom", String(150))
    source_url: Mapped[str | None] = mapped_column(String(500))
    updated_on: Mapped[date] = mapped_column("mis_a_jour_le", Date)
    is_active: Mapped[bool] = mapped_column("active", Boolean, default=True)


class PracticalGuideTranslationRow(Base):
    __tablename__ = "fiche_pratique_traduction"

    guide_id: Mapped[int] = mapped_column(
        "id_fiche", Integer, ForeignKey("fiche_pratique.id_fiche"), primary_key=True
    )
    language: Mapped[str] = mapped_column("code_langue", String(10), ForeignKey("langue.code"), primary_key=True)
    title: Mapped[str] = mapped_column("titre", String(150))
    introduction: Mapped[str] = mapped_column(String(500))
    source_name: Mapped[str | None] = mapped_column("source_nom", String(150))


class PracticalGuideStepRow(Base):
    """One step of a guide, in one language (French included): a guide is read
    entirely in one language, never mixed."""

    __tablename__ = "fiche_pratique_etape"

    guide_id: Mapped[int] = mapped_column(
        "id_fiche", Integer, ForeignKey("fiche_pratique.id_fiche"), primary_key=True
    )
    language: Mapped[str] = mapped_column("code_langue", String(10), ForeignKey("langue.code"), primary_key=True)
    position: Mapped[int] = mapped_column("ordre", SmallInteger, primary_key=True)
    text: Mapped[str] = mapped_column("texte", String(300))


class PracticalGuideItemRow(Base):
    """Something to bring, in one language (French included)."""

    __tablename__ = "fiche_pratique_a_apporter"

    guide_id: Mapped[int] = mapped_column(
        "id_fiche", Integer, ForeignKey("fiche_pratique.id_fiche"), primary_key=True
    )
    language: Mapped[str] = mapped_column("code_langue", String(10), ForeignKey("langue.code"), primary_key=True)
    position: Mapped[int] = mapped_column("ordre", SmallInteger, primary_key=True)
    text: Mapped[str] = mapped_column("texte", String(150))
