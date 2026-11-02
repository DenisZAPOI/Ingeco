"""
The served zone: communes, address search, and the check that a stop is
inside the pilot zone (H18).
"""

from sqlalchemy.orm import Session

from ..repository import commune_repository, place_repository
from ..repository.commune_repository import Commune
from ..repository.place_repository import Place, PlacesUnavailable
from ..utils import database
from ..utils.errors import ServiceUnavailable, UnprocessableEntity

# Centre of Cayenne. The communes chosen by the user are the real rule; this
# radius only catches a position that cannot belong to them (Kourou typed
# with "Cayenne"). An API setting, as the contract allows (H18).
PILOT_ZONE_CENTRE = (4.9372, -52.3260)
PILOT_ZONE_RADIUS_KM = 20.0

SEARCH_UNAVAILABLE = "La recherche d'adresses ne répond pas pour le moment. Réessayez dans quelques minutes."


def list_communes() -> list[Commune]:
    with database.session() as session:
        return commune_repository.list_communes(session)


def search_places(text: str, commune_id: int) -> list[Place]:
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
