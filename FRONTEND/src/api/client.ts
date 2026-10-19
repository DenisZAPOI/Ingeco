// The only fetch of the project. Every API call goes through here: base URL,
// session cookie, timeout and error translation are handled in one place.

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:5000';

// On a weak network a request can hang for minutes: better to fail and offer
// a retry than to leave the user in front of an endless spinner.
const TIMEOUT_MS = 15_000;

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

export async function request<T>(method: Method, path: string, body?: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      // The session cookie is HttpOnly: the browser sends it, JavaScript never reads it.
      credentials: 'include',
      headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch {
    throw new ApiError(0, 'Network unreachable');
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const payload: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const { error, detail } = readErrorPayload(payload);
    throw new ApiError(response.status, error ?? response.statusText, detail);
  }
  return payload as T;
}

function readErrorPayload(payload: unknown): { error: string | null; detail: unknown } {
  if (typeof payload === 'object' && payload !== null && 'error' in payload) {
    const { error, detail } = payload as { error: unknown; detail?: unknown };
    return { error: typeof error === 'string' ? error : null, detail: detail ?? null };
  }
  return { error: null, detail: payload };
}
