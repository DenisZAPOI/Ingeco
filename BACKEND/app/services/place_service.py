"""
The served zone: communes, address search, and the check that a stop is
in a served commune (H18, zones set by the administrator) and was proposed by this API (audit F9).
"""

import base64
import hashlib
import hmac

from sqlalchemy.orm import Session

from ..repository import commune_repository, place_repository, ride_repository
from ..repository.commune_repository import Commune
from ..repository.place_repository import Place, PlacesUnavailable
from ..utils import database
from ..utils.errors import ServiceUnavailable, TooManyRequests, UnprocessableEntity
from ..utils.rate_limit import AttemptLimiter

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

# "Vos derniers lieux" at the top of a booking step: a few, to stay a short
# list on a phone. Ten rides are read to find them: trips often repeat
# (home, work), so fewer could give only one or two different places.
MAX_RECENT_PLACES = 3
RECENT_RIDES_READ = 10
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
        return commune_repository.list_communes(session, served_only=True)


def search_places(text: str, commune_id: int, *, user_id: int) -> list[Place]:
    count_lookup(user_id)
    with database.session() as session:
        commune = _served_commune(session, commune_id)
        try:
            return place_repository.search(session, text, commune.id, commune.name)
        except PlacesUnavailable:
            raise ServiceUnavailable(SEARCH_UNAVAILABLE) from None


def recent_places(rider_id: int) -> list[Place]:
    """The last places a rider went from or to, to book the same trip again in one tap.

    Read from their rides, without calling OpenRouteService. A place of a
    commune no longer served is left out: it could not be booked.
    """
    with database.session() as session:
        stops = ride_repository.find_recent_stops(session, rider_id, RECENT_RIDES_READ)
        served_ids = {commune.id for commune in commune_repository.list_communes(session, served_only=True)}

    places: list[Place] = []
    seen_addresses: set[str] = set()
    for stop in stops:
        is_new = stop.address not in seen_addresses
        is_served = stop.commune_id in served_ids
        if is_new and is_served:
            places.append(Place(label=stop.address, lat=stop.lat, lng=stop.lng, commune_id=stop.commune_id))
            seen_addresses.add(stop.address)
        if len(places) == MAX_RECENT_PLACES:
            break
    return places


def check_served(session: Session, lat: float, lng: float, commune_id: int) -> None:
    """Raises 422 if the stop is not in a served commune.

    The served communes are the rule (set by the administrator). The commune
    of a stop comes from OpenRouteService and is signed with it
    (check_proposed); the rectangle only catches a position that cannot be
    in French Guiana at all.
    """
    _served_commune(session, commune_id)
    if not place_repository.in_search_area(lat, lng):
        raise UnprocessableEntity(_out_of_zone(session))


def _served_commune(session: Session, commune_id: int) -> Commune:
    commune = commune_repository.find_by_id(session, commune_id)
    if commune is None or not commune.served:
        raise UnprocessableEntity(_out_of_zone(session))
    return commune


def _out_of_zone(session: Session) -> str:
    names = [commune.name for commune in commune_repository.list_communes(session, served_only=True)]
    served = ", ".join(names[:-1]) + " et " + names[-1] if len(names) > 1 else "".join(names)
    return f"Nous ne desservons pas encore cette adresse. Le service couvre {served}."
