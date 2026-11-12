"""Accounts and reference data: role, commune, utilisateur, usager, chauffeur,
vehicule, demande_suppression (sql/schema-mvp.sql, migrations 001, 002 and 010),
piece_chauffeur and chauffeur_commune (migration 024)."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, Boolean, Date, ForeignKey, Integer, LargeBinary, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from ..utils.database import Base
from .types import UtcDateTime

# MEDIUMBLOB in the schema: up to 16 MB, the API keeps a photo under 100 KB.
_MEDIUMBLOB_BYTES = 16 * 1024 * 1024 - 1


class Role(Base):
    __tablename__ = "role"

    code: Mapped[str] = mapped_column(String(20), primary_key=True)
    label: Mapped[str] = mapped_column("libelle", String(100))


class Commune(Base):
    """One of the 22 communes of French Guiana (migration 010). Only the served
    ones receive rides; offers and help services can be anywhere."""

    __tablename__ = "commune"

    id: Mapped[int] = mapped_column("id_commune", Integer, primary_key=True)
    name: Mapped[str] = mapped_column("nom", String(100), unique=True)
    # Set by the administrator (zones, M9); provisional: the pilot zone
    is_served: Mapped[bool] = mapped_column("desservie", Boolean, default=False)


class UserRow(Base):
    """Account shared by every role. `status`: 'actif', 'suspendu' or 'supprime'.

    A deleted account (migration 025) is anonymised, the database checks it:
    empty names, no email, password nor code, phone '+000' + 9-digit id.
    """

    __tablename__ = "utilisateur"

    id: Mapped[int] = mapped_column("id_utilisateur", Integer, primary_key=True)
    role: Mapped[str] = mapped_column("code_role", String(20), ForeignKey("role.code"))
    status: Mapped[str] = mapped_column("statut", String(20))
    first_name: Mapped[str] = mapped_column("prenom", String(100))
    last_name: Mapped[str] = mapped_column("nom", String(100))
    phone: Mapped[str] = mapped_column("telephone", String(16), unique=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str | None] = mapped_column("mot_de_passe_hash", String(255))
    activation_code_hash: Mapped[str | None] = mapped_column("code_activation_hash", String(255))
    activation_code_expires_at: Mapped[datetime | None] = mapped_column("code_activation_expire_le", UtcDateTime)
    created_at: Mapped[datetime] = mapped_column("cree_le", UtcDateTime)
    # Migration 001 (audit F3): a new password or a suspension ends older sessions.
    session_version: Mapped[int] = mapped_column("version_session", Integer, default=0)


class RiderRow(Base):
    __tablename__ = "usager"

    user_id: Mapped[int] = mapped_column(
        "id_utilisateur", Integer, ForeignKey("utilisateur.id_utilisateur"), primary_key=True
    )
    is_priority: Mapped[bool] = mapped_column("est_prioritaire", Boolean, default=False)
    needs_accessible_vehicle: Mapped[bool] = mapped_column("besoin_vehicule_accessible", Boolean, default=False)


class DriverRow(Base):
    """Last known position only, no history (H6); the photo is read on its own route."""

    __tablename__ = "chauffeur"

    user_id: Mapped[int] = mapped_column(
        "id_utilisateur", Integer, ForeignKey("utilisateur.id_utilisateur"), primary_key=True
    )
    is_available: Mapped[bool] = mapped_column("est_disponible", Boolean, default=False)
    last_lat: Mapped[Decimal | None] = mapped_column("derniere_lat", DECIMAL(9, 6))
    last_lng: Mapped[Decimal | None] = mapped_column("derniere_lng", DECIMAL(9, 6))
    last_location_at: Mapped[datetime | None] = mapped_column("derniere_position_le", UtcDateTime)
    # deferred: a list of drivers never loads the images.
    photo: Mapped[bytes | None] = mapped_column(LargeBinary(_MEDIUMBLOB_BYTES), deferred=True)
    photo_updated_at: Mapped[datetime | None] = mapped_column("photo_modifiee_le", UtcDateTime)


class VehicleRow(Base):
    """One vehicle per driver in the MVP (H5)."""

    __tablename__ = "vehicule"

    id: Mapped[int] = mapped_column("id_vehicule", Integer, primary_key=True)
    driver_id: Mapped[int] = mapped_column(
        "id_chauffeur", Integer, ForeignKey("chauffeur.id_utilisateur"), unique=True
    )
    plate: Mapped[str] = mapped_column("immatriculation", String(20), unique=True)
    model: Mapped[str] = mapped_column("modele", String(100))
    seats: Mapped[int] = mapped_column("nombre_places", SmallInteger)
    is_accessible: Mapped[bool] = mapped_column("est_accessible", Boolean, default=False)


class DeletionRequest(Base):
    """Migration 002: a request to delete an account, handled by an administrator.

    `demande_en_cours` is a column computed by MySQL (one open request per
    account): never written, so not mapped.
    """

    __tablename__ = "demande_suppression"

    id: Mapped[int] = mapped_column("id_demande", Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column("id_utilisateur", Integer, ForeignKey("utilisateur.id_utilisateur"))
    requested_at: Mapped[datetime] = mapped_column("demandee_le", UtcDateTime)
    handled_at: Mapped[datetime | None] = mapped_column("traitee_le", UtcDateTime)
    handled_by_id: Mapped[int | None] = mapped_column(
        "id_traitee_par", Integer, ForeignKey("utilisateur.id_utilisateur")
    )


class DriverDocumentRow(Base):
    """A document of the driver, CHECKED IN PERSON by an administrator: no file
    and no number is kept, only its type and expiry (minimisation, §2). A
    renewal is a new row; the document in force of a type is the one that
    expires last. `expires_on` is the last valid day."""

    __tablename__ = "piece_chauffeur"

    id: Mapped[int] = mapped_column("id_piece", Integer, primary_key=True)
    driver_id: Mapped[int] = mapped_column("id_chauffeur", Integer, ForeignKey("chauffeur.id_utilisateur"))
    kind: Mapped[str] = mapped_column("type", String(30))
    expires_on: Mapped[date] = mapped_column("expire_le", Date)
    checked_at: Mapped[datetime] = mapped_column("verifiee_le", UtcDateTime)
    checked_by_id: Mapped[int] = mapped_column(
        "id_verifiee_par", Integer, ForeignKey("utilisateur.id_utilisateur")
    )


class DriverCommuneRow(Base):
    """A commune where the driver agrees to drive. No row = the whole served
    zone; only served communes make sense (rule of the API)."""

    __tablename__ = "chauffeur_commune"

    driver_id: Mapped[int] = mapped_column(
        "id_chauffeur", Integer, ForeignKey("chauffeur.id_utilisateur"), primary_key=True
    )
    commune_id: Mapped[int] = mapped_column(
        "id_commune", Integer, ForeignKey("commune.id_commune"), primary_key=True
    )
