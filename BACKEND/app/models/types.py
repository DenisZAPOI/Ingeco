"""Column types shared by the models."""

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator


class UtcDateTime(TypeDecorator[datetime]):
    """A DATETIME column holding UTC, read and written as an aware datetime.

    The schema stores UTC without a time zone (DATETIME), the API works with
    aware datetimes in UTC (ride_rules.now()). Writing converts to UTC and
    drops the zone; reading puts the UTC zone back. A datetime without a zone
    is refused: it would be read back at the wrong hour.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, _dialect) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("A datetime written to the database must carry its time zone (UTC).")
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, _dialect) -> datetime | None:
        return value.replace(tzinfo=timezone.utc) if value is not None else None
