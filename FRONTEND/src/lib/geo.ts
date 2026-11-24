// Distances on the Earth's surface, without a library.

const EARTH_RADIUS_M = 6_371_000;
const DEGREES_TO_RADIANS = Math.PI / 180;

export type LatLng = { lat: number; lng: number };

/** Haversine formula: straight-line distance in metres. */
export function distanceMeters(from: LatLng, to: LatLng): number {
  const lat1 = from.lat * DEGREES_TO_RADIANS;
  const lat2 = to.lat * DEGREES_TO_RADIANS;
  const deltaLat = lat2 - lat1;
  const deltaLng = (to.lng - from.lng) * DEGREES_TO_RADIANS;
  const a = Math.sin(deltaLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(deltaLng / 2) ** 2;
  return 2 * EARTH_RADIUS_M * Math.asin(Math.sqrt(a));
}

/** Opens the GPS app the driver chose on their phone (geo: link, Android). No
 *  route is computed here, and no third party gets the rider's address unless
 *  the driver's own app is one (audit RGPD R9). */
export function directionsUrl({ lat, lng }: LatLng): string {
  return `geo:${lat},${lng}?q=${lat},${lng}`;
}

/** Without a GPS app answering geo: links (iPhone, computer): the map of OpenStreetMap. */
export function mapUrl({ lat, lng }: LatLng): string {
  return `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lng}#map=${OSM_ZOOM}/${lat}/${lng}`;
}

// Close enough to see the street.
const OSM_ZOOM = 17;
