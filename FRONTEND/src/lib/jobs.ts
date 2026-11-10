import type { ContractType, JobOffer, Schedule } from '../api/jobs';
import { language, t } from '../i18n';

// Job offers (module M2): the filters run on the phone, over the list loaded
// once (GET /jobs). They live in the address, so the Back button from an
// offer comes back to the same filtered list.

export const SCHEDULES: readonly Schedule[] = ['day', 'shifted', 'night'];

export type JobFilters = {
  /** A commune id, or null for every commune. */
  communeId: number | null;
  schedule: Schedule | null;
  beginnerWelcome: boolean;
  noDiplomaRequired: boolean;
};

export const NO_FILTER: JobFilters = { communeId: null, schedule: null, beginnerWelcome: false, noDiplomaRequired: false };

// Names of the address parameters, in French: users see them.
const PARAMS = { commune: 'commune', schedule: 'horaires', beginner: 'debutant', noDiploma: 'sans-diplome' } as const;
const YES = '1';

export function filterJobOffers(offers: readonly JobOffer[], filters: JobFilters): JobOffer[] {
  return offers.filter(
    (offer) =>
      (filters.communeId === null || offer.place.communeId === filters.communeId) &&
      (filters.schedule === null || offer.schedule === filters.schedule) &&
      (!filters.beginnerWelcome || offer.beginnerWelcome) &&
      (!filters.noDiplomaRequired || offer.noDiplomaRequired),
  );
}

/** The communes that have at least one offer, sorted by name: the choices of the filter. */
export function offerCommunes(offers: readonly JobOffer[]): { id: number; name: string }[] {
  const byId = new Map(offers.map((offer) => [offer.place.communeId, offer.communeName]));
  return [...byId].map(([id, name]) => ({ id, name })).sort((a, b) => a.name.localeCompare(b.name, 'fr'));
}

export function filtersFromParams(params: URLSearchParams): JobFilters {
  const commune = Number(params.get(PARAMS.commune));
  const schedule = params.get(PARAMS.schedule);
  return {
    communeId: Number.isInteger(commune) && commune > 0 ? commune : null,
    schedule: SCHEDULES.find((value) => value === schedule) ?? null,
    beginnerWelcome: params.get(PARAMS.beginner) === YES,
    noDiplomaRequired: params.get(PARAMS.noDiploma) === YES,
  };
}

export function filtersToParams(filters: JobFilters): Record<string, string> {
  const params: Record<string, string> = {};
  if (filters.communeId !== null) params[PARAMS.commune] = String(filters.communeId);
  if (filters.schedule !== null) params[PARAMS.schedule] = filters.schedule;
  if (filters.beginnerWelcome) params[PARAMS.beginner] = YES;
  if (filters.noDiplomaRequired) params[PARAMS.noDiploma] = YES;
  return params;
}

export function scheduleLabel(schedule: Schedule): string {
  return t(`jobs.schedule.${schedule}`);
}

export function contractLabel(contract: ContractType): string {
  return t(`jobs.contract.${contract}`);
}

// The last list received, shown at once on the next visit while the API
// confirms it (no wait when the app is opened again). Kept with its
// language: after a change of language, the list in the old one is not shown.

const STORAGE_KEY = 'job-offers';

export function readStoredJobOffers(): JobOffer[] | null {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? 'null');
    if (typeof parsed !== 'object' || parsed === null) return null;
    const { language: storedIn, offers } = parsed as { language: unknown; offers: unknown };
    if (storedIn === language() && Array.isArray(offers) && offers.every(isJobOffer)) {
      return offers;
    }
  } catch {
    // Storage blocked or corrupted: no head start.
  }
  return null;
}

export function storeJobOffers(offers: JobOffer[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ language: language(), offers }));
  } catch {
    // Storage blocked: fetched again next time.
  }
}

/** Enough to draw a card and book: an offer kept by an older version is dropped. */
function isJobOffer(value: unknown): value is JobOffer {
  if (typeof value !== 'object' || value === null) return false;
  const { id, title, place, schedule } = value as Record<string, unknown>;
  return (
    typeof id === 'number' &&
    typeof title === 'string' &&
    typeof schedule === 'string' &&
    typeof place === 'object' &&
    place !== null &&
    typeof (place as Record<string, unknown>).token === 'string'
  );
}

/** The offer handed over by the list (router state), if it is this one. */
export function offerFromState(state: unknown, id: number): JobOffer | null {
  if (typeof state !== 'object' || state === null || !('offer' in state)) return null;
  const { offer } = state as { offer: unknown };
  return isJobOffer(offer) && offer.id === id ? offer : null;
}
