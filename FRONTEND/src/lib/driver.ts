import type { RideStatus } from '../api/rides';

/** What the driver reads at the top of a ride ("course", their word). */
export const DRIVER_STATUS_HEADLINES: Record<RideStatus, string> = {
  awaiting_payment: "Course pas encore payée par l'usager",
  pending: 'Course proposée',
  accepted: 'Allez chercher le passager',
  in_progress: 'Passager à bord',
  completed: 'Course terminée',
  cancelled: 'Course annulée',
  expired: 'Course expirée',
};

/** Short state of a ride in the driver's lists. */
export const DRIVER_STATUS_LABELS: Record<RideStatus, string> = {
  awaiting_payment: 'Non payée',
  pending: 'À prendre',
  accepted: 'Acceptée',
  in_progress: 'En cours',
  completed: 'Terminée',
  cancelled: 'Annulée',
  expired: 'Expirée',
};
