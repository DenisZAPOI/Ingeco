"""
Addresses and road distances, from OpenRouteService (H13), on OpenStreetMap
data.

The only place that talks to that service: switching provider only changes
this file. Without a key (ORS_API_KEY empty: development without an account,
tests, CI), a short list of public places of the pilot zone and a straight-line
distance stretched to look like a road one. No call to the Internet then.
"""

import json
import logging
import math
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Place:
    label: str
    lat: float
    lng: float
    commune_id: int


class PlacesUnavailable(Exception):
    """OpenRouteService did not answer, or answered something unusable."""


MAX_RESULTS = 8
EARTH_RADIUS_KM = 6371.0
METRES_PER_KM = 1000

# --- OpenRouteService --------------------------------------------------------
ORS_BASE_URL = "https://api.openrouteservice.org"
ORS_GEOCODE_PATH = "/geocode/search"
ORS_ROUTE_PATH = "/v2/directions/driving-car/json"
# Short: the user waits behind it, on a 2G network that already costs seconds.
ORS_TIMEOUT_SECONDS = 5
# Asked for more than shown: some are dropped by the commune filter.
ORS_SEARCH_SIZE = 20
# Rectangle around the pilot zone (Cayenne, Rémire-Montjoly, Matoury), and the
# point results are ranked from.
SEARCH_AREA = {"min_lon": -52.50, "min_lat": 4.75, "max_lon": -52.20, "max_lat": 5.00}
SEARCH_FOCUS = (4.9372, -52.3260)

_api_key: str | None = None


def configure(api_key: str | None) -> None:
    """Called once at startup with ORS_API_KEY. None: fake data."""
    global _api_key
    _api_key = api_key or None
    if _api_key is None:
        logger.warning("ORS_API_KEY is empty: addresses and distances are FAKE data, see .env.example")


def search(_session: Session, text: str, commune_id: int, commune_name: str) -> list[Place]:
    """Places of the commune matching the text typed, best first.

    Raises PlacesUnavailable if the external service fails.
    """
    if _api_key is None:
        return _fake_search(text, commune_id)

    features = _call_ors(
        "GET",
        ORS_GEOCODE_PATH,
        {
            "text": text,
            "size": ORS_SEARCH_SIZE,
            "boundary.rect.min_lon": SEARCH_AREA["min_lon"],
            "boundary.rect.min_lat": SEARCH_AREA["min_lat"],
            "boundary.rect.max_lon": SEARCH_AREA["max_lon"],
            "boundary.rect.max_lat": SEARCH_AREA["max_lat"],
            "focus.point.lat": SEARCH_FOCUS[0],
            "focus.point.lon": SEARCH_FOCUS[1],
        },
    ).get("features", [])

    wanted = _simplify(commune_name)
    places = []
    for feature in features:
        properties = feature.get("properties", {})
        # Only the commune the user chose: OSM writes it as the locality or,
        # for a place outside the town centre, as the local administration.
        communes = {_simplify(properties.get(key) or "") for key in ("locality", "localadmin")}
        if wanted not in communes:
            continue
        lng, lat = feature["geometry"]["coordinates"]
        places.append(Place(label=properties["label"], lat=lat, lng=lng, commune_id=commune_id))
    return places[:MAX_RESULTS]


def road_distance_km(from_lat: float, from_lng: float, to_lat: float, to_lng: float) -> float:
    """Driving distance. Raises PlacesUnavailable if the external service fails."""
    if _api_key is None:
        return straight_distance_km(from_lat, from_lng, to_lat, to_lng) * _FAKE_ROAD_DETOUR_FACTOR

    answer = _call_ors("POST", ORS_ROUTE_PATH, {"coordinates": [[from_lng, from_lat], [to_lng, to_lat]]})
    try:
        return answer["routes"][0]["summary"]["distance"] / METRES_PER_KM
    except (KeyError, IndexError, TypeError):
        logger.error("OpenRouteService route without distance", extra={"context": {"path": ORS_ROUTE_PATH}})
        raise PlacesUnavailable("route without distance") from None


def straight_distance_km(from_lat: float, from_lng: float, to_lat: float, to_lng: float) -> float:
    """Haversine formula: distance on the Earth's surface."""
    lat1, lat2 = math.radians(from_lat), math.radians(to_lat)
    delta_lat = lat2 - lat1
    delta_lng = math.radians(to_lng - from_lng)
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def _call_ors(method: str, path: str, data: dict) -> dict:
    url = ORS_BASE_URL + path
    headers = {"Authorization": _api_key, "Accept": "application/json"}
    body = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(data)
    else:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"

    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, data=body, headers=headers, method=method), timeout=ORS_TIMEOUT_SECONDS
        ) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        # The URL holds the text typed (an address): never in the logs, only the path.
        logger.error("OpenRouteService refused the call", extra={"context": {"path": path, "status": error.code}})
        raise PlacesUnavailable(str(error.code)) from None
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        logger.error("OpenRouteService unreachable", extra={"context": {"path": path, "reason": type(error).__name__}})
        raise PlacesUnavailable(type(error).__name__) from None


def _simplify(text: str) -> str:
    """'Éboué' → 'eboue': users type without accents on a phone keyboard."""
    without_accents = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode()
    return without_accents.lower()


# --- Fake data (no key) ------------------------------------------------------
# Public places only, with approximate positions: no one's home address.
_FAKE_PLACES = (
    Place("Place des Palmistes, Cayenne", 4.9389, -52.3326, 1),
    Place("Mairie de Cayenne, place Léopold Héder", 4.9372, -52.3260, 1),
    Place("Hôpital de Cayenne (centre hospitalier), avenue des Flamboyants", 4.9310, -52.3190, 1),
    Place("Gare routière, Cayenne", 4.9354, -52.3277, 1),
    Place("Marché de Cayenne, rue Lalouette", 4.9363, -52.3297, 1),
    Place("Préfecture, rue Fiedmont, Cayenne", 4.9385, -52.3350, 1),
    Place("Mairie de Rémire-Montjoly", 4.9165, -52.2700, 2),
    Place("Plage de Montjoly, Rémire-Montjoly", 4.9230, -52.2790, 2),
    Place("Zone d'activités de Dégrad-des-Cannes, Rémire-Montjoly", 4.8590, -52.2760, 2),
    Place("Mairie de Matoury", 4.8470, -52.3310, 3),
    Place("Aéroport Félix Éboué, Matoury", 4.8197, -52.3604, 3),
    Place("Centre commercial Collery, Matoury", 4.8840, -52.3170, 3),
)
# Roads are never straight: in town, about a third longer than the crow flies.
_FAKE_ROAD_DETOUR_FACTOR = 1.3


def _fake_search(text: str, commune_id: int) -> list[Place]:
    words = _simplify(text).split()
    found = [
        place
        for place in _FAKE_PLACES
        if place.commune_id == commune_id and all(word in _simplify(place.label) for word in words)
    ]
    return found[:MAX_RESULTS]
