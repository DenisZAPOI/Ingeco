"""
Rules on a ride: statuses, delays, price.

Pure functions and constants, shared by the booking, the DTOs and the tests.
The delays are API settings, not data (contract 3.3): nothing is stored.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

# --- Values of the API (contract 3.3) ----------------------------------------
PURPOSES = ("employment", "training", "health", "administrative", "other")

AWAITING_PAYMENT = "awaiting_payment"
PENDING = "pending"
ACCEPTED = "accepted"
IN_PROGRESS = "in_progress"
COMPLETED = "completed"
CANCELLED = "cancelled"
EXPIRED = "expired"
STATUSES = (AWAITING_PAYMENT, PENDING, ACCEPTED, IN_PROGRESS, COMPLETED, CANCELLED, EXPIRED)

PAYMENT_NOT_REQUIRED = "not_required"
PAYMENT_PENDING = "pending"
PAYMENT_PAID = "paid"
PAYMENT_REFUNDED = "refunded"
PAYMENT_STATUSES = (PAYMENT_NOT_REQUIRED, PAYMENT_PENDING, PAYMENT_PAID, PAYMENT_REFUNDED)

APP_CHANNEL = "app"
PHONE_CHANNEL = "phone"
CHANNELS = (APP_CHANNEL, PHONE_CHANNEL)

# --- Delays (contract 6.8) ---------------------------------------------------
# A scheduled ride leaves a driver the time to plan it.
MIN_SCHEDULING_DELAY = timedelta(minutes=30)
# Time to pay (H16), and time for a driver to take an immediate ride.
PAYMENT_DELAY = timedelta(minutes=15)
DRIVER_SEARCH_DELAY = timedelta(minutes=15)

TOO_SOON = (
    "L'heure de départ doit être au moins 30 minutes après maintenant. "
    "Pour partir plus tôt, choisissez « Maintenant »."
)


def now() -> datetime:
    """The current time, in UTC. One place, so the tests can move the clock."""
    return datetime.now(timezone.utc)


def check_scheduled_at(scheduled_at: datetime | None) -> datetime | None:
    """None is an immediate ride; otherwise at least 30 minutes from now."""
    if scheduled_at is None:
        return None
    if scheduled_at < now() + MIN_SCHEDULING_DELAY:
        raise ValueError(TOO_SOON)
    return scheduled_at.astimezone(timezone.utc)


# --- Price (contract 3.6, UC12) ----------------------------------------------
# The distance shown to the user is rounded to 100 m: the price is computed
# from that same figure, so they can check it themselves.
DISTANCE_DECIMALS = Decimal("0.1")
_CENT = Decimal("1")


def round_distance(distance_km: float) -> Decimal:
    return Decimal(str(distance_km)).quantize(DISTANCE_DECIMALS, rounding=ROUND_HALF_UP)


def price_cents(base_fare_cents: int, per_km_cents: int, distance_km: Decimal) -> int:
    """Pick-up fare + price per kilometre, rounded to the nearest cent."""
    return base_fare_cents + int((per_km_cents * distance_km).quantize(_CENT, rounding=ROUND_HALF_UP))


# --- Lists of rides (UC17) ---------------------------------------------------
# Not finished yet: the "À venir" tab. Few at a time, so never paginated.
UPCOMING_STATUSES = (AWAITING_PAYMENT, PENDING, ACCEPTED, IN_PROGRESS)
# Over: the "Passés" tab, paginated.
PAST_STATUSES = (COMPLETED, CANCELLED, EXPIRED)
PAST_PAGE_SIZE = 20

# --- Open rides of a rider (audit F6) ----------------------------------------
# Not finished yet, at the same time: a trip now, and a few booked ahead (an
# appointment and its return). To confirm with the client.
MAX_OPEN_IMMEDIATE_RIDES = 1
MAX_OPEN_SCHEDULED_RIDES = 3

# --- Cancellation (UC16) -----------------------------------------------------
# Before the rider is on board (contract 3.3).
CANCELLABLE_STATUSES = (AWAITING_PAYMENT, PENDING, ACCEPTED)

# --- Rating (UC18) -----------------------------------------------------------
MIN_SCORE = 1
MAX_SCORE = 5
RATING_COMMENT_MAX_LENGTH = 500

TOO_LONG_COMMENT = f"Le commentaire ne doit pas dépasser {RATING_COMMENT_MAX_LENGTH} caractères."


def clean_comment(raw: str | None) -> str | None:
    """An empty comment means "no comment": stored as null, never as ''."""
    if raw is None or not raw.strip():
        return None
    comment = raw.strip()
    if len(comment) > RATING_COMMENT_MAX_LENGTH:
        raise ValueError(TOO_LONG_COMMENT)
    return comment


# --- Driver side (UC20 to UC27) ----------------------------------------------
# Immediate rides shown to a driver: within this distance of their position.
# Covers the whole pilot zone from Cayenne.
OFFER_RADIUS_KM = 10.0
# Older, a position says nothing of where the driver is (phone asleep, app in
# the background): the driver is then treated as without position.
LOCATION_MAX_AGE = timedelta(minutes=5)
# A driver holds one active ride at a time; the rides they accept must be at
# least this far apart (contract 3.3, "course active").
RIDE_SPACING = timedelta(minutes=60)
# A scheduled ride can be started this long before its time, not earlier.
START_WINDOW = RIDE_SPACING
# Rider and driver may call each other only while the ride is under way.
CONTACT_STATUSES = (ACCEPTED, IN_PROGRESS)
# What a driver holds: counts for their timetable.
HELD_STATUSES = (ACCEPTED, IN_PROGRESS)


def ride_time(scheduled_at: datetime | None, at: datetime) -> datetime:
    """When a ride takes the driver: its scheduled time, or now for an immediate one."""
    return scheduled_at or at


def too_close(new_time: datetime, held_times: list[datetime]) -> bool:
    """A ride at `new_time` would overlap one already held."""
    return any(abs(new_time - held) < RIDE_SPACING for held in held_times)


# --- Driver's earnings (UC28) ------------------------------------------------
# Guyana time (America/Cayenne): UTC-3 all year, no daylight saving time. A
# day of earnings is a day there, whatever the server's time zone.
GUYANA_TIME = timezone(timedelta(hours=-3))
# A month at most: the screen offers today, this week and this month.
EARNINGS_MAX_DAYS = 31
EARNINGS_PERIOD_TOO_LONG = f"La période ne peut pas dépasser {EARNINGS_MAX_DAYS} jours."
EARNINGS_PERIOD_REVERSED = "La date de fin doit être après la date de début."


def check_earnings_period(first_day: date, last_day: date) -> None:
    """ValueError if the period is reversed or longer than a month."""
    if last_day < first_day:
        raise ValueError(EARNINGS_PERIOD_REVERSED)
    if (last_day - first_day).days + 1 > EARNINGS_MAX_DAYS:
        raise ValueError(EARNINGS_PERIOD_TOO_LONG)


def guyana_day_start(day: date) -> datetime:
    """Midnight of `day` in Guyana, as an aware datetime."""
    return datetime.combine(day, datetime.min.time(), tzinfo=GUYANA_TIME)
