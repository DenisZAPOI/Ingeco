import type { Role, User } from '../api/auth';

// Who was logged in last time on this phone. At startup, the session takes a
// round trip to the API (three if the access token has expired): on 2G, more
// than a second of waiting. With this hint, the right screen is drawn at once
// and the API only confirms it.
//
// Only what the first screen needs: the phone may be shared, nothing personal
// beyond a first name is kept. Erased at logout and when the API says nobody
// is logged in.

const STORAGE_KEY = 'session-hint';

export type SessionHint = { firstName: string; role: Role };

const ROLES: readonly Role[] = ['rider', 'driver', 'partner', 'operator', 'admin'];

export function readSessionHint(): SessionHint | null {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? 'null');
    if (isSessionHint(parsed)) {
      return parsed;
    }
  } catch {
    // Storage blocked (private browsing) or corrupted value: no hint.
  }
  return null;
}

export function saveSessionHint(user: User | null): void {
  try {
    if (user) {
      const hint: SessionHint = { firstName: user.firstName, role: user.role };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(hint));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  } catch {
    // Storage blocked: the app works the same, only without the head start.
  }
}

function isSessionHint(value: unknown): value is SessionHint {
  if (typeof value !== 'object' || value === null) return false;
  const { firstName, role } = value as Record<string, unknown>;
  return typeof firstName === 'string' && ROLES.includes(role as Role);
}
