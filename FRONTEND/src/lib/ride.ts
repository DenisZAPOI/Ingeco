import type { Purpose, Ride, RideStatus } from '../api/rides';
import { guyanaDateTime } from './format';

// Words of the rider (charter, part 7): "trajet", never "course".

export const PURPOSE_LABELS: Record<Purpose, string> = {
  employment: 'Emploi (entretien, travail)',
  training: 'Formation',
  health: 'Soins (médecin, hôpital)',
  administrative: 'Démarche administrative',
  other: 'Autre',
};

export const PURPOSES = Object.keys(PURPOSE_LABELS) as Purpose[];

/** What the rider reads at the top of their trip. */
export const STATUS_HEADLINES: Record<RideStatus, string> = {
  awaiting_payment: 'En attente de votre paiement',
  pending: 'Nous cherchons un chauffeur',
  accepted: 'Un chauffeur a accepté votre trajet',
  in_progress: 'Vous êtes en route',
  completed: 'Trajet terminé',
  cancelled: 'Trajet annulé',
  expired: "Ce trajet n'a pas pu avoir lieu",
};

// Same rule as the API (services/ride_rules.py): checked here first to spare
// a round trip, the API decides.
const MIN_SCHEDULING_DELAY_MS = 30 * 60 * 1000;

/** Message for a day and time that cannot be booked, or null. */
export function scheduleError(day: string, time: string): string | null {
  if (!day || !time) {
    return "Indiquez le jour et l'heure de départ.";
  }
  if (new Date(guyanaDateTime(day, time)).getTime() < Date.now() + MIN_SCHEDULING_DELAY_MS) {
    return "L'heure de départ doit être au moins 30 minutes après maintenant. Pour partir plus tôt, choisissez « Maintenant ».";
  }
  return null;
}

/** Why a trip expired: not paid in time (nothing was charged), or no driver
 *  took it (the payment is refunded). Read from the payment state. */
export function expiryReason(ride: Ride): string {
  return ride.paymentStatus === 'refunded'
    ? "Aucun chauffeur n'était disponible à temps. Nous en sommes désolés."
    : "Le paiement n'a pas été fait dans les 15 minutes : la réservation a été annulée. Rien n'a été prélevé.";
}

/** The time limit to pay is part of the ride, not a guess of the phone. */
export function canStillPay(ride: Ride): boolean {
  return ride.status === 'awaiting_payment' && new Date(ride.expiresAt).getTime() > Date.now();
}

/** The ride handed over by the previous screen (navigation state), if it is this one. */
export function rideFromState(state: unknown, id: number): Ride | null {
  if (typeof state !== 'object' || state === null || !('ride' in state)) return null;
  const { ride } = state as { ride: unknown };
  return typeof ride === 'object' && ride !== null && (ride as Ride).id === id ? (ride as Ride) : null;
}

/** Short state of a trip in a list. */
export const STATUS_LABELS: Record<RideStatus, string> = {
  awaiting_payment: 'À payer',
  pending: "Recherche d'un chauffeur",
  accepted: 'Chauffeur trouvé',
  in_progress: 'En route',
  completed: 'Terminé',
  cancelled: 'Annulé',
  expired: 'Expiré',
};

// Same rule as the API (CANCELLABLE_STATUSES): before the rider is on board.
const CANCELLABLE: readonly RideStatus[] = ['awaiting_payment', 'pending', 'accepted'];

export function canCancel(ride: Ride): boolean {
  return CANCELLABLE.includes(ride.status);
}

export function canRate(ride: Ride): boolean {
  return ride.status === 'completed' && ride.rating === null;
}

const OVER: readonly RideStatus[] = ['completed', 'cancelled', 'expired'];

/** Finished, cancelled or expired: nothing more will happen. */
export function isOver(ride: Ride): boolean {
  return OVER.includes(ride.status);
}

/** When the trip leaves: its scheduled time, or its booking time for an immediate one. */
export function rideDate(ride: Ride): string {
  return ride.scheduledAt ?? ride.createdAt;
}

// Same bounds as the API (services/ride_rules.py).
export const SCORES = [1, 2, 3, 4, 5] as const;
export const RATING_COMMENT_MAX_LENGTH = 500;
