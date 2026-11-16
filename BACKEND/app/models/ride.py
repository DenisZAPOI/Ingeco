"""Rides and what goes with them: tarif, course, evaluation (sql/schema-mvp.sql),
horaire_service (migration 018), etape_course (migration 023)."""

from datetime import datetime, time
from decimal import Decimal

from sqlalchemy import DECIMAL, Boolean, CHAR, ForeignKey, Integer, SmallInteger, String, Time, UniqueConstraint
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
    """A ride. The ENUM values stay in French: 'en_attente', 'emploi', 'paye'…

    Statuses added by migration 020: 'chauffeur_arrive' (needs `arrived_at`)
    and 'passager_absent' (final, needs `absent_at`); payment 'echoue' keeps
    the ride in 'attente_paiement' so the rider can try again.
    """

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
    # Free landmark ("devant la pharmacie"), NULL rather than empty
    pickup_landmark: Mapped[str | None] = mapped_column("repere_depart", String(255))
    dropoff_address: Mapped[str] = mapped_column("adresse_arrivee", String(255))
    dropoff_lat: Mapped[Decimal] = mapped_column("lat_arrivee", DECIMAL(9, 6))
    dropoff_lng: Mapped[Decimal] = mapped_column("lng_arrivee", DECIMAL(9, 6))
    dropoff_commune_id: Mapped[int] = mapped_column("id_commune_arrivee", Integer, ForeignKey("commune.id_commune"))
    dropoff_landmark: Mapped[str | None] = mapped_column("repere_arrivee", String(255))

    scheduled_at: Mapped[datetime | None] = mapped_column("prevue_le", UtcDateTime)
    needs_accessible_vehicle: Mapped[bool] = mapped_column("besoin_vehicule_accessible", Boolean)
    # 1 to 8, as vehicule.nombre_places: offered only to vehicles with enough seats
    passengers: Mapped[int] = mapped_column("nombre_passagers", SmallInteger, default=1)
    with_luggage: Mapped[bool] = mapped_column("avec_bagages", Boolean, default=False)
    distance_km: Mapped[Decimal] = mapped_column(DECIMAL(6, 2))
    tariff_id: Mapped[int] = mapped_column("id_tarif", Integer, ForeignKey("tarif.id_tarif"))
    price_cents: Mapped[int] = mapped_column("prix_centimes", Integer)
    payment_status: Mapped[str] = mapped_column("statut_paiement", String(20))
    expires_at: Mapped[datetime] = mapped_column("expire_le", UtcDateTime)

    created_at: Mapped[datetime] = mapped_column("cree_le", UtcDateTime)
    paid_at: Mapped[datetime | None] = mapped_column("payee_le", UtcDateTime)
    accepted_at: Mapped[datetime | None] = mapped_column("acceptee_le", UtcDateTime)
    # Driver at the pickup point; may stay NULL if they start without saying so
    arrived_at: Mapped[datetime | None] = mapped_column("arrivee_le", UtcDateTime)
    started_at: Mapped[datetime | None] = mapped_column("demarree_le", UtcDateTime)
    completed_at: Mapped[datetime | None] = mapped_column("terminee_le", UtcDateTime)
    cancelled_at: Mapped[datetime | None] = mapped_column("annulee_le", UtcDateTime)
    expired_at: Mapped[datetime | None] = mapped_column("expiree_le", UtcDateTime)
    absent_at: Mapped[datetime | None] = mapped_column("absent_le", UtcDateTime)
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


class ServiceHoursRow(Base):
    """A time slot when a ride can be requested, set by the administrator.

    LOCAL TIME of Cayenne, unlike every DATETIME of the schema (UTC): convert
    the request time before comparing. Both ends included (23:59:59 for "until
    midnight"); no row for a day = closed that day. Overlapping slots of one
    day are refused by the API, not by the database.
    """

    __tablename__ = "horaire_service"
    __table_args__ = (UniqueConstraint("jour_semaine", "ouvre_a"),)

    id: Mapped[int] = mapped_column("id_horaire", Integer, primary_key=True)
    # 1 = Monday … 7 = Sunday (ISO 8601)
    weekday: Mapped[int] = mapped_column("jour_semaine", SmallInteger)
    opens_at: Mapped[time] = mapped_column("ouvre_a", Time)
    closes_at: Mapped[time] = mapped_column("ferme_a", Time)


class RideStepRow(Base):
    """Log of a ride: one row per step, with its author (NULL = the application:
    expiry, periodic task). Written in the same transaction as the change of
    the ride, never updated nor deleted by the API. An 'incident' needs a
    comment, which never holds health data (§12)."""

    __tablename__ = "etape_course"

    id: Mapped[int] = mapped_column("id_etape", Integer, primary_key=True)
    ride_id: Mapped[int] = mapped_column("id_course", Integer, ForeignKey("course.id_course"))
    author_id: Mapped[int | None] = mapped_column("id_auteur", Integer, ForeignKey("utilisateur.id_utilisateur"))
    kind: Mapped[str] = mapped_column("type", String(20))
    happened_at: Mapped[datetime] = mapped_column("survenue_le", UtcDateTime)
    comment: Mapped[str | None] = mapped_column("commentaire", String(500))
