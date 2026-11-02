// Paths of the booking flow, in French: users see them in the address bar.
// One step = one path, so the phone's Back button goes to the previous step.

export const BOOKING_PATHS = {
  pickup: '/reserver/depart',
  dropoff: '/reserver/arrivee',
  time: '/reserver/horaire',
  confirm: '/reserver/confirmation',
} as const;

export function ridePath(id: number): string {
  return `/trajets/${id}`;
}

export function paymentPath(id: number): string {
  return `/trajets/${id}/paiement`;
}

export const RIDES_PATH = '/trajets';

// Driver side: "course", their own word (charter, part 7).
export const DRIVER_RIDES_PATH = '/courses';

export function driverRidePath(id: number): string {
  return `/courses/${id}`;
}
