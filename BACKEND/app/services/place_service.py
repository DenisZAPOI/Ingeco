"""
The served zone: communes, address search, and the check that a stop is
inside the pilot zone (H18) and was proposed by this API (audit F9).
"""

import base64
import hashlib
import hmac

from sqlalchemy.orm import Session

from ..repository import commune_repository, place_repository
from ..repository.commune_repository import Commune
from ..repository.place_repository import Place, PlacesUnavailable
from ..utils import database
from ..utils.errors import ServiceUnavailable, TooManyRequests, UnprocessableEntity
from ..utils.rate_limit import AttemptLimiter

# Centre of Cayenne. The communes chosen by the user are the real rule; this
# radius only catches a position that cannot belong to them (Kourou typed
# with "Cayenne"). An API setting, as the contract allows (H18).
PILOT_ZONE_CENTRE = (4.9372, -52.3260)
PILOT_ZONE_RADIUS_KM = 20.0

SEARCH_UNAVAILABLE = "La recherche d'adresses ne répond pas pour le moment. Réessayez dans quelques minutes."

# Address searches and trip estimates each call OpenRouteService, whose quota is
# shared by everyone (audit F6). Far more than a booking needs (a few letters
# typed, an estimate or two), far less than a loop.
MAX_LOOKUPS_PER_ACCOUNT = 60
LOOKUP_WINDOW_SECONDS = 10 * 60
TOO_MANY_LOOKUPS = "Trop de recherches d'un coup. Réessayez dans quelques minutes."
lookups = AttemptLimiter(MAX_LOOKUPS_PER_ACCOUNT, LOOKUP_WINDOW_SECONDS)

# Every place this API proposes (GET /places) or shows (a ride's stops) comes
# with a signature of its label, position and commune. A stop is accepted only
# with it: the label shown to the driver is the one of that position, never a
# text typed apart from it ("Aéroport" placed next door, to pay less).
PLACE_NOT_PROPOSED = "Choisissez l'adresse dans la liste proposée."
_SIGNING_PURPOSE = b"places"
_signing_key: bytes | None = None


def configure(*, signing_key: str) -> None:
    """Called once at startup with the application's secret key."""
    global _signing_key
    # A key of its own, derived: a place signature is never valid elsewhere.
    _signing_key = hmac.new(signing_key.encode(), _SIGNING_PURPOSE, hashlib.sha256).digest()


def place_token(address: str, lat: float, lng: float, commune_id: int) -> str:
    if _signing_key is None:
        raise RuntimeError("place_service.configure(...) must be called at startup.")
    # repr: the shortest text that reads back as the same float, as JSON does.
    message = f"{address}\n{lat!r}\n{lng!r}\n{commune_id}".encode()
    digest = hmac.new(_signing_key, message, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def check_proposed(address: str, lat: float, lng: float, commune_id: int, token: str | None) -> None:
    """Raises 422 unless the stop is a place this API proposed, unchanged."""
    expected = place_token(address, lat, lng, commune_id)
    if token is None or not hmac.compare_digest(expected, token):
        raise UnprocessableEntity(PLACE_NOT_PROPOSED)


def count_lookup(user_id: int) -> None:
    """One more call to the address service for this account, or 429."""
    if not lookups.try_record(str(user_id)):
        raise TooManyRequests(TOO_MANY_LOOKUPS)


def list_communes() -> list[Commune]:
    with database.session() as session:
        return commune_repository.list_communes(session)


def search_places(text: str, commune_id: int, *, user_id: int) -> list[Place]:
    count_lookup(user_id)
    with database.session() as session:
        commune = _served_commune(session, commune_id)
        try:
            return place_repository.search(session, text, commune.id, commune.name)
        except PlacesUnavailable:
            raise ServiceUnavailable(SEARCH_UNAVAILABLE) from None


def check_served(session: Session, lat: float, lng: float, commune_id: int) -> None:
    """Raises 422 if the stop is outside the pilot zone."""
    _served_commune(session, commune_id)
    if place_repository.straight_distance_km(*PILOT_ZONE_CENTRE, lat, lng) > PILOT_ZONE_RADIUS_KM:
        raise UnprocessableEntity(_out_of_zone(session))


def _served_commune(session: Session, commune_id: int) -> Commune:
    commune = commune_repository.find_by_id(session, commune_id)
    if commune is None:
        raise UnprocessableEntity(_out_of_zone(session))
    return commune


def _out_of_zone(session: Session) -> str:
    names = [commune.name for commune in commune_repository.list_communes(session)]
    served = ", ".join(names[:-1]) + " et " + names[-1] if len(names) > 1 else "".join(names)
    return f"Nous ne desservons pas encore cette adresse. Le service couvre {served}."
