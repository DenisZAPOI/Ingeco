"""Rides and what goes with them: tarif, course, evaluation (sql/schema-mvp.sql)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, Boolean, CHAR, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from ..utils.database import Base
from .types import UtcDateTime


class TariffRow(Base):
    """One active tariff in the MVP (H8); old ones stay, rides keep theirs.

    `tarif_actif` is a column computed by MySQL (one active tariff at most):
    never written, so not mapped.
    """

    __tablename__ = "tarif"

    id: Mapped[int] = mapped_column("id_tarif", Integer, primary_key=True)
    base_fare_cents: Mapped[int] = mapped_column("prise_en_charge_centimes", Integer)
    per_km_cents: Mapped[int] = mapped_column("prix_km_centimes", Integer)
    is_active: Mapped[bool] = mapped_column("actif", Boolean)
    created_at: Mapped[datetime] = mapped_column("cree_le", UtcDateTime)


class RideRow(Base):
    """A ride. The ENUM values stay in French: 'en_attente', 'emploi', 'paye'…"""

    __tablename__ = "course"

    id: Mapped[int] = mapped_column("id_course", Integer, primary_key=True)
    client_request_id: Mapped[str] = mapped_column("id_requete_client", CHAR(36), unique=True)
    rider_id: Mapped[int] = mapped_column("id_usager", Integer, ForeignKey("usager.id_utilisateur"))
    driver_id: Mapped[int | None] = mapped_column("id_chauffeur", Integer, ForeignKey("chauffeur.id_utilisateur"))
    booked_by_id: Mapped[int] = mapped_column("id_saisie_par", Integer, ForeignKey("utilisateur.id_utilisateur"))
    channel: Mapped[str] = mapped_column("canal", String(20))
    status: Mapped[str] = mapped_column("statut", String(20))
    purpose: Mapped[str] = mapped_column("motif", String(30))

    pickup_address: Mapped[str] = mapped_column("adresse_depart", String(255))
    pickup_lat: Mapped[Decimal] = mapped_column("lat_depart", DECIMAL(9, 6))
    pickup_lng: Mapped[Decimal] = mapped_column("lng_depart", DECIMAL(9, 6))
    pickup_commune_id: Mapped[int] = mapped_column("id_commune_depart", Integer, ForeignKey("commune.id_commune"))
    dropoff_address: Mapped[str] = mapped_column("adresse_arrivee", String(255))
    dropoff_lat: Mapped[Decimal] = mapped_column("lat_arrivee", DECIMAL(9, 6))
    dropoff_lng: Mapped[Decimal] = mapped_column("lng_arrivee", DECIMAL(9, 6))
    dropoff_commune_id: Mapped[int] = mapped_column("id_commune_arrivee", Integer, ForeignKey("commune.id_commune"))

    scheduled_at: Mapped[datetime | None] = mapped_column("prevue_le", UtcDateTime)
    needs_accessible_vehicle: Mapped[bool] = mapped_column("besoin_vehicule_accessible", Boolean)
    distance_km: Mapped[Decimal] = mapped_column(DECIMAL(6, 2))
    tariff_id: Mapped[int] = mapped_column("id_tarif", Integer, ForeignKey("tarif.id_tarif"))
    price_cents: Mapped[int] = mapped_column("prix_centimes", Integer)
    payment_status: Mapped[str] = mapped_column("statut_paiement", String(20))
    expires_at: Mapped[datetime] = mapped_column("expire_le", UtcDateTime)

    created_at: Mapped[datetime] = mapped_column("cree_le", UtcDateTime)
    paid_at: Mapped[datetime | None] = mapped_column("payee_le", UtcDateTime)
    accepted_at: Mapped[datetime | None] = mapped_column("acceptee_le", UtcDateTime)
    started_at: Mapped[datetime | None] = mapped_column("demarree_le", UtcDateTime)
    completed_at: Mapped[datetime | None] = mapped_column("terminee_le", UtcDateTime)
    cancelled_at: Mapped[datetime | None] = mapped_column("annulee_le", UtcDateTime)
    expired_at: Mapped[datetime | None] = mapped_column("expiree_le", UtcDateTime)
    cancelled_by_id: Mapped[int | None] = mapped_column(
        "id_annulee_par", Integer, ForeignKey("utilisateur.id_utilisateur")
    )


class RatingRow(Base):
    """One rating at most per ride: the ride is the key."""

    __tablename__ = "evaluation"

    ride_id: Mapped[int] = mapped_column("id_course", Integer, ForeignKey("course.id_course"), primary_key=True)
    score: Mapped[int] = mapped_column("note", SmallInteger)
    comment: Mapped[str | None] = mapped_column("commentaire", String(500))
    created_at: Mapped[datetime] = mapped_column("cree_le", UtcDateTime)
