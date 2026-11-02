import { distanceMeters, type LatLng } from './geo';

// When the phone sends the driver's position (decided 02/11/2026): at most
// every 30 s, and only after a move of 50 m. A position older than 5 minutes
// is ignored by the API, so a driver who does not move sends it again after 4.
export const SEND_INTERVAL_MS = 30_000;
const MIN_MOVE_M = 50;
const KEEP_ALIVE_MS = 4 * 60_000;

export type Sent = { position: LatLng; at: number };

/** Whether `position`, known at `now`, is worth a call. */
export function shouldSend(position: LatLng, now: number, last: Sent | null): boolean {
  if (last === null) return true;
  if (now - last.at >= KEEP_ALIVE_MS) return true;
  return now - last.at >= SEND_INTERVAL_MS && distanceMeters(last.position, position) >= MIN_MOVE_M;
}
