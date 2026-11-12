"""
ORM models: one class per table, inheriting from utils.database.Base.

The schema belongs to the DB team (parcours C): sql/schema-mvp.sql, then the
files of sql/migrations/ in order. A model describes a table that ALREADY
exists there, column for column. Never create, alter or migrate a table from
this repo; if a feature needs a schema change, write the request for the DB
team instead (GitHub issue labelled `bd`).

Names: the tables and columns are in French (the DB team's choice), the Python
classes and attributes in English (the project's convention). The
correspondence is written here once: `scheduled_at = mapped_column("prevue_le")`.
The values of the ENUM columns stay in French in the rows ('en_attente'); the
repositories translate them.

tests/test_models.py checks every model against the real tables.
"""

from .account import (
    Commune,
    DeletionRequest,
    DriverCommuneRow,
    DriverDocumentRow,
    DriverRow,
    RiderRow,
    Role,
    UserRow,
    VehicleRow,
)
from .content import (
    HelpServiceLanguageRow,
    HelpServiceRow,
    HelpServiceTranslationRow,
    JobOfferRow,
    JobOfferTranslationRow,
    LanguageRow,
    PracticalGuideItemRow,
    PracticalGuideRow,
    PracticalGuideStepRow,
    PracticalGuideTranslationRow,
)
from .orientation import ActionPlanRow, AnswerRow, PlanStepRow, QuestionnaireRow
from .ride import RatingRow, RideRow, RideStepRow, ServiceHoursRow, TariffRow
from .support import SupportRequestRow

__all__ = [
    "ActionPlanRow",
    "AnswerRow",
    "Commune",
    "DeletionRequest",
    "DriverCommuneRow",
    "DriverDocumentRow",
    "DriverRow",
    "HelpServiceLanguageRow",
    "HelpServiceRow",
    "HelpServiceTranslationRow",
    "JobOfferRow",
    "JobOfferTranslationRow",
    "LanguageRow",
    "PlanStepRow",
    "PracticalGuideItemRow",
    "PracticalGuideRow",
    "PracticalGuideStepRow",
    "PracticalGuideTranslationRow",
    "QuestionnaireRow",
    "RatingRow",
    "RideRow",
    "RideStepRow",
    "RiderRow",
    "Role",
    "ServiceHoursRow",
    "SupportRequestRow",
    "TariffRow",
    "UserRow",
    "VehicleRow",
]
