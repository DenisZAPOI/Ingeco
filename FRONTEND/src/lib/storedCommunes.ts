import type { Commune } from '../api/places';

// The served communes almost never change: the last list received is shown
// at once, and the API only confirms it (no wait on the second visit).

const STORAGE_KEY = 'communes';

export function readStoredCommunes(): Commune[] | null {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? 'null');
    if (Array.isArray(parsed) && parsed.every(isCommune)) {
      return parsed;
    }
  } catch {
    // Storage blocked or corrupted: no head start.
  }
  return null;
}

export function storeCommunes(communes: Commune[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(communes));
  } catch {
    // Storage blocked: fetched again next time.
  }
}

function isCommune(value: unknown): value is Commune {
  if (typeof value !== 'object' || value === null) return false;
  const { id, name } = value as Record<string, unknown>;
  return typeof id === 'number' && typeof name === 'string';
}
