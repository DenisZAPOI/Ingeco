// Account access, for a visitor.
export const LOGIN_PATH = '/connexion';

/** The page a visitor was sent to log in from. Only a path of this app: a
 *  value from elsewhere ("//site.example") never leads out of it. */
export function returnPathFromState(state: unknown): string | null {
  if (typeof state !== 'object' || state === null || !('returnTo' in state)) return null;
  const { returnTo } = state as { returnTo: unknown };
  return typeof returnTo === 'string' && returnTo.startsWith('/') && !returnTo.startsWith('//') && !returnTo.startsWith('/\\')
    ? returnTo
    : null;
}
export const PROFILE_PATH = '/profil';
export const ACTIVATION_PATH = '/activation';
export const PASSWORD_RESET_PATH = '/mot-de-passe-oublie';

/** The number a reset code was just sent to, handed to the activation page
 *  in the router state (never in the address: it is personal data). */
export function sentPhoneFromState(state: unknown): string | null {
  if (typeof state !== 'object' || state === null || !('sentTo' in state)) return null;
  const { sentTo } = state as { sentTo: unknown };
  return typeof sentTo === 'string' ? sentTo : null;
}

// Paths of the booking flow, in French: users see them in the address bar.
// One step = one path, so the phone's Back button goes to the previous step.

/** Start of a booking: goes to its first step (a visitor logs in first). */
export const BOOKING_START_PATH = '/reserver';

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
/** "J'ai besoin d'aide": the help page, which leads to the questions and the call center. */
export const HELP_PATH = '/aide';
export const FAQ_PATH = '/aide/questions';
/** Directory of help services (module M5), public: the needs, then the list. */
export const HELP_SERVICES_PATH = '/aide/services';

export function helpServicePath(id: number): string {
  return `/aide/services/${id}`;
}

// Job offers (module M2), public: a visitor reads them without an account.
export const JOBS_PATH = '/emplois';

/** Training (module M3), public, reached from the job offers. */
export const TRAININGS_PATH = '/formations';

export function jobPath(id: number): string {
  return `/emplois/${id}`;
}
