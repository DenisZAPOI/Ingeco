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

export const EARNINGS_PATH = '/revenus';

export function driverRidePath(id: number): string {
  return `/courses/${id}`;
}

// Administration: "comptes", the word of its screens.
export const ADMIN_ACCOUNTS_PATH = '/admin/comptes';
export const NEW_ACCOUNT_PATH = '/admin/comptes/nouveau';

// Public, linked from the footer of every screen.
export const ABOUT_PATH = '/a-propos';
