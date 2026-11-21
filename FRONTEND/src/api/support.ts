import { request } from './client';

/** « Être rappelé »: someone of the structure calls this number back. */
export function requestCallback(phone: string): Promise<void> {
  return request<void>('POST', '/help-requests/callback', { phone });
}
