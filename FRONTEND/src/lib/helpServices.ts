import type { HelpCategory, HelpService, SpokenLanguage } from '../api/helpServices';
import type { Purpose } from '../api/rides';
import { language, t } from '../i18n';
import { formatDay } from './format';

// Directory of help services (module M5): the filters run on the phone, over
// the list loaded once (GET /help-services). The need and the commune live in
// the address, so the Back button from a service comes back to the same list.

/** The needs, in the order of the cahier des charges (§7.5). */
export const HELP_CATEGORIES: readonly HelpCategory[] = [
  'childcare',
  'housing',
  'rights',
  'health',
  'food',
  'digital',
  'paperwork',
  'equipment',
];

export type HelpFilters = {
  category: HelpCategory | null;
  /** A commune id, or null for every commune. */
  communeId: number | null;
};

// Names of the address parameters, in French: users see them.
const PARAMS = { category: 'besoin', commune: 'commune' } as const;

/** The need as written in the address ("garde"), and back. French: users see it. */
const CATEGORY_SLUGS: Record<HelpCategory, string> = {
  childcare: 'garde',
  housing: 'logement',
  rights: 'droits',
  health: 'sante',
  food: 'alimentation',
  digital: 'numerique',
  paperwork: 'demarches',
  equipment: 'equipement',
};

export function filtersFromParams(params: URLSearchParams): HelpFilters {
  const slug = params.get(PARAMS.category);
  const commune = Number(params.get(PARAMS.commune));
  return {
    category: HELP_CATEGORIES.find((category) => CATEGORY_SLUGS[category] === slug) ?? null,
    communeId: Number.isInteger(commune) && commune > 0 ? commune : null,
  };
}

export function filtersToParams(filters: HelpFilters): Record<string, string> {
  const params: Record<string, string> = {};
  if (filters.category !== null) params[PARAMS.category] = CATEGORY_SLUGS[filters.category];
  if (filters.communeId !== null) params[PARAMS.commune] = String(filters.communeId);
  return params;
}

export function filterHelpServices(services: readonly HelpService[], filters: HelpFilters): HelpService[] {
  return services.filter(
    (service) =>
      (filters.category === null || service.category === filters.category) &&
      (filters.communeId === null || service.place.communeId === filters.communeId),
  );
}

/** The communes that have at least one service, sorted by name: the choices of the filter. */
export function serviceCommunes(services: readonly HelpService[]): { id: number; name: string }[] {
  const byId = new Map(services.map((service) => [service.place.communeId, service.communeName]));
  return [...byId].map(([id, name]) => ({ id, name })).sort((a, b) => a.name.localeCompare(b.name, 'fr'));
}

export function categoryLabel(category: HelpCategory): string {
  return t(`helpServices.categories.${category}.title`);
}

export function languageLabel(code: SpokenLanguage): string {
  return t(`helpServices.languageNames.${code}`);
}

/** The language of the app, when the service speaks it and it is not French
 *  (every service speaks French): shown as "Parle créole guyanais". */
export function speaksAppLanguage(service: HelpService): SpokenLanguage | null {
  const current = language();
  const spoken = service.spokenLanguages.find((code) => code === current);
  return spoken && spoken !== 'fr' ? spoken : null;
}

/** '2026-11-02' → 'lundi 2 novembre'. A date without time: read at noon UTC,
 *  so that it stays the same day in Guyana time (UTC−3). */
export function formatUpdatedOn(day: string): string {
  return formatDay(`${day}T12:00:00Z`);
}

/** The purpose of a trip to a service: health care, or a procedure. */
export function purposeFor(category: HelpCategory): Purpose {
  return category === 'health' ? 'health' : 'administrative';
}

export type Simulator = { id: 'mesDroitsSociaux' | 'unJeuneUneSolution'; url: string };

/** Official simulators of the benefits one is entitled to (cahier des charges
 *  §7.5), shown with the "rights" services. Addresses checked on 11/11/2026. */
export const RIGHTS_SIMULATORS: readonly Simulator[] = [
  // Every benefit, for everyone (State and social protection bodies).
  { id: 'mesDroitsSociaux', url: 'https://www.mesdroitssociaux.gouv.fr/' },
  // Benefits for people aged 16 to 30 (scenario A: Jordan, 22).
  { id: 'unJeuneUneSolution', url: 'https://www.1jeune1solution.gouv.fr/mes-aides' },
];

// The last list received, shown at once on the next visit while the API
// confirms it. Kept with its language, like the job offers (ADR 018).

const STORAGE_KEY = 'help-services';

export function readStoredHelpServices(): HelpService[] | null {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? 'null');
    if (typeof parsed !== 'object' || parsed === null) return null;
    const { language: storedIn, services } = parsed as { language: unknown; services: unknown };
    if (storedIn === language() && Array.isArray(services) && services.every(isHelpService)) {
      return services;
    }
  } catch {
    // Storage blocked or corrupted: no head start.
  }
  return null;
}

export function storeHelpServices(services: HelpService[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ language: language(), services }));
  } catch {
    // Storage blocked: fetched again next time.
  }
}

/** Enough to draw a card and book: a service kept by an older version is dropped. */
function isHelpService(value: unknown): value is HelpService {
  if (typeof value !== 'object' || value === null) return false;
  const { id, name, category, place, spokenLanguages } = value as Record<string, unknown>;
  return (
    typeof id === 'number' &&
    typeof name === 'string' &&
    HELP_CATEGORIES.some((known) => known === category) &&
    Array.isArray(spokenLanguages) &&
    typeof place === 'object' &&
    place !== null &&
    typeof (place as Record<string, unknown>).token === 'string'
  );
}

/** The service handed over by the list (router state), if it is this one. */
export function serviceFromState(state: unknown, id: number): HelpService | null {
  if (typeof state !== 'object' || state === null || !('service' in state)) return null;
  const { service } = state as { service: unknown };
  return isHelpService(service) && service.id === id ? service : null;
}
