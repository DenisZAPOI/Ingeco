"""Help requests (module M0): demande_aide (migration 027)."""

from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..utils.database import Base
from .types import UtcDateTime


class SupportRequestRow(Base):
    """"Être rappelé" ('rappel') or "Signaler un problème" ('signalement').

    Someone without an account can ask to be called back: `user_id` is NULL and
    `phone` is then required. Only a report can concern a ride. Handled by an
    administrator or an operator, never deleted. The message never holds
    health data (§12), and no emergency service is promised (§6).
    """

    __tablename__ = "demande_aide"

    id: Mapped[int] = mapped_column("id_demande", Integer, primary_key=True)
    kind: Mapped[str] = mapped_column("type", String(20))
    user_id: Mapped[int | None] = mapped_column("id_utilisateur", Integer, ForeignKey("utilisateur.id_utilisateur"))
    # Number to call back, international format as utilisateur.telephone
    phone: Mapped[str | None] = mapped_column("telephone", String(16))
    ride_id: Mapped[int | None] = mapped_column("id_course", Integer, ForeignKey("course.id_course"))
    message: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column("creee_le", UtcDateTime)
    handled_at: Mapped[datetime | None] = mapped_column("traitee_le", UtcDateTime)
    handled_by_id: Mapped[int | None] = mapped_column(
        "id_traitee_par", Integer, ForeignKey("utilisateur.id_utilisateur")
    )
