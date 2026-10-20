// The only fetch of the project. Every API call goes through here: base URL,
// session cookies, CSRF header, silent session renewal, timeout and error
// translation are handled in one place.

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:5000';

// On a weak network a request can hang for minutes: better to fail and offer
// a retry than to leave the user in front of an endless spinner.
const TIMEOUT_MS = 15_000;

const UNAUTHORIZED = 401;
const NO_CONTENT = 204;
const REFRESH_PATH = '/auth/refresh';
// These answer 401 for a wrong password or an ended session: renewing the
// session there would make no sense.
const NO_RENEWAL_PATHS = new Set(['/auth/login', '/auth/register', '/auth/activate', '/auth/logout', REFRESH_PATH]);

// The session tokens are HttpOnly cookies, out of JavaScript's reach. Next to
// them the API sets readable CSRF cookies, copied into this header on every
// write: a site that forges a request cannot read them, so cannot copy them.
const CSRF_HEADER = 'X-CSRF-TOKEN';
const ACCESS_CSRF_COOKIE = 'csrf_access_token';
const REFRESH_CSRF_COOKIE = 'csrf_refresh_token';

/** Error returned by the API ({ error, detail }), or network failure (status 0).
 *  A body outside the error format (503 of /health) is kept whole in `detail`. */
export class ApiError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor(status: number, message: string, detail: unknown = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

type Method = 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';

// Called when the session cannot be renewed: the session context then shows
// the visitor screens. Set by SessionProvider.
let sessionExpiredListener: () => void = () => {};

export function onSessionExpired(listener: () => void): void {
  sessionExpiredListener = listener;
}

export type StoredSession = 'none' | 'expired' | 'active';

/** What the session cookies say, without a call. Each CSRF cookie lives exactly
 *  as long as its HttpOnly token: no refresh one means nobody is logged in, no
 *  access one means the 15 minutes are over. On 2G, each call avoided saves a
 *  third of a second or more. */
export function storedSession(): StoredSession {
  if (!readCookie(REFRESH_CSRF_COOKIE)) return 'none';
  return readCookie(ACCESS_CSRF_COOKIE) ? 'active' : 'expired';
}

export async function request<T>(method: Method, path: string, body?: unknown): Promise<T> {
  try {
    return await send<T>(method, path, body);
  } catch (error) {
    if (
      !(error instanceof ApiError) ||
      error.status !== UNAUTHORIZED ||
      NO_RENEWAL_PATHS.has(path) ||
      storedSession() === 'none'
    ) {
      throw error;
    }
    // The access token lasts 15 minutes: renew it once, then replay the call.
    if (!(await renewSession())) {
      sessionExpiredListener();
      throw error;
    }
    return send<T>(method, path, body);
  }
}

// Several calls failing at the same moment share one renewal.
let pendingRenewal: Promise<boolean> | null = null;

function renewSession(): Promise<boolean> {
  pendingRenewal ??= send('POST', REFRESH_PATH)
    .then(() => true)
    .catch(() => false)
    .finally(() => {
      pendingRenewal = null;
    });
  return pendingRenewal;
}

async function send<T>(method: Method, path: string, body?: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      credentials: 'include',
      headers: buildHeaders(method, path, body),
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch {
    throw new ApiError(0, 'Network unreachable');
  }

  if (response.status === NO_CONTENT) {
    return undefined as T;
  }

  const payload: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const { error, detail } = readErrorPayload(payload);
    throw new ApiError(response.status, error ?? response.statusText, detail);
  }
  return payload as T;
}

function buildHeaders(method: Method, path: string, body: unknown): Record<string, string> {
  const headers: Record<string, string> = {};
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }
  if (method !== 'GET') {
    const csrfToken = readCookie(path === REFRESH_PATH ? REFRESH_CSRF_COOKIE : ACCESS_CSRF_COOKIE);
    if (csrfToken) {
      headers[CSRF_HEADER] = csrfToken;
    }
  }
  return headers;
}

function readCookie(name: string): string | null {
  const prefix = `${name}=`;
  const cookie = document.cookie.split('; ').find((entry) => entry.startsWith(prefix));
  return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
}

function readErrorPayload(payload: unknown): { error: string | null; detail: unknown } {
  if (typeof payload === 'object' && payload !== null && 'error' in payload) {
    const { error, detail } = payload as { error: unknown; detail?: unknown };
    return { error: typeof error === 'string' ? error : null, detail: detail ?? null };
  }
  return { error: null, detail: payload };
}
