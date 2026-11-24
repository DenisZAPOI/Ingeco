import type { Purpose, Ride, Stop } from '../api/rides';

// The booking being typed, step by step. Kept in sessionStorage: it survives
// a reload or the phone's Back button, and disappears with the tab (a shared
// phone does not keep someone else's addresses).

const STORAGE_KEY = 'booking-draft';

export type When = 'now' | 'later';

export type BookingDraft = {
  pickup: Stop | null;
  dropoff: Stop | null;
  purpose: Purpose | null;
  when: When;
  /** 'YYYY-MM-DD' and 'HH:MM', in Guyana time, when `when` is 'later'. */
  day: string;
  time: string;
  /** Created at the confirmation, reused by every retry of that booking. */
  requestId: string | null;
  /** Set by "Comment y aller ?" on a job offer: the drop-off is the job's
   *  place, so the drop-off step is skipped (3 steps instead of 4). */
  jobOfferId: number | null;
  /** Set by "Comment y aller ?" on a help service, in the same way. */
  helpServiceId: number | null;
};

const EMPTY_DRAFT: BookingDraft = {
  pickup: null,
  dropoff: null,
  purpose: null,
  when: 'now',
  day: '',
  time: '',
  requestId: null,
  jobOfferId: null,
  helpServiceId: null,
};

export function readBookingDraft(): BookingDraft {
  try {
    const parsed: unknown = JSON.parse(sessionStorage.getItem(STORAGE_KEY) ?? 'null');
    if (typeof parsed === 'object' && parsed !== null) {
      const draft = { ...EMPTY_DRAFT, ...(parsed as Partial<BookingDraft>) };
      // A stop kept by an older version of the app has no token: chosen again.
      const dropoff = signedOrNull(draft.dropoff);
      return {
        ...draft,
        pickup: signedOrNull(draft.pickup),
        dropoff,
        jobOfferId: dropoff ? draft.jobOfferId : null,
        helpServiceId: dropoff ? draft.helpServiceId : null,
      };
    }
  } catch {
    // Storage blocked or corrupted: start again.
  }
  return EMPTY_DRAFT;
}

/** A stop as a ride or the storage gives it, with a token if it has one. */
type MaybeSignedStop = Omit<Stop, 'token'> & { token?: string | null };

function signedOrNull(stop: MaybeSignedStop | null): Stop | null {
  if (stop === null || typeof stop.token !== 'string') return null;
  return { ...stop, token: stop.token };
}

export function saveBookingDraft(draft: BookingDraft | null): void {
  try {
    if (draft) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
    } else {
      sessionStorage.removeItem(STORAGE_KEY);
    }
  } catch {
    // Storage blocked: the draft lives in memory only.
  }
}

/** A new booking of the same trip (an expired one): same places and purpose,
 *  the time still to choose. A new request id: it is another booking. */
export function draftFromRide(ride: Ride): BookingDraft {
  // The rider always gets signed stops; a stop without its token (only a
  // commune, audit RGPD R5) is chosen again.
  return { ...EMPTY_DRAFT, pickup: signedOrNull(ride.pickup), dropoff: signedOrNull(ride.dropoff), purpose: ride.purpose };
}

/** "Comment y aller ?" on a job offer: the trip to the job, for work. Only
 *  the pickup and the time are left to choose (cahier des charges §18: a trip
 *  in 3 actions at most from an offer). */
export function draftForJobOffer(jobOfferId: number, place: Stop): BookingDraft {
  return { ...EMPTY_DRAFT, dropoff: place, purpose: 'employment', jobOfferId };
}

/** "Comment y aller ?" on a help service: the trip there, for care or a
 *  procedure. Only the pickup and the time are left, as from a job offer. */
export function draftForHelpService(helpServiceId: number, place: Stop, purpose: Purpose): BookingDraft {
  return { ...EMPTY_DRAFT, dropoff: place, purpose, helpServiceId };
}

/** "Réserver un trajet" from the action plan: only the purpose is known. */
export function draftForPurpose(purpose: Purpose): BookingDraft {
  return { ...EMPTY_DRAFT, purpose };
}

/** Whether the drop-off step is skipped: it was given by a job offer or a help service. */
export function skipsDropoff(draft: BookingDraft): boolean {
  return (draft.jobOfferId !== null || draft.helpServiceId !== null) && draft.dropoff !== null;
}

/** The place given by "Comment y aller ?", forgotten: the usual 4 steps. */
export const NO_GIVEN_DROPOFF = { jobOfferId: null, helpServiceId: null } as const;

/** The number of each step shown in "Étape 2 sur 3", and their total. */
export function bookingSteps(draft: BookingDraft): { pickup: number; dropoff: number; time: number; confirm: number; total: number } {
  return skipsDropoff(draft)
    ? { pickup: 1, dropoff: 0, time: 2, confirm: 3, total: 3 }
    : { pickup: 1, dropoff: 2, time: 3, confirm: 4, total: 4 };
}
