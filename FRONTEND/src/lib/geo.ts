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

/** Opens the phone's GPS app (Google Maps on Android and iPhone, its site otherwise). No route is computed here. */
export function directionsUrl({ lat, lng }: LatLng): string {
  return `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
}
