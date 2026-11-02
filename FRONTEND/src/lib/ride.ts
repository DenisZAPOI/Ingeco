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
