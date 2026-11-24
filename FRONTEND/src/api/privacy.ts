import type { components } from '../types/api';
import { ApiError, request } from './client';

// The person's rights on their data (audit RGPD R3) and the requests the staff handles (R10).

export type MyData = components['schemas']['MyDataDto'];
export type HelpRequest = components['schemas']['HelpRequestDto'];
export type DeletionRequest = components['schemas']['DeletionRequestDto'];
export type OpenDeletionRequest = components['schemas']['DeletionRequestItemDto'];
export type Callback = components['schemas']['CallbackDto'];

const NOT_FOUND = 404;

/** « Mes données » : everything the application keeps about the logged-in person. */
export function fetchMyData(): Promise<MyData> {
  return request<MyData>('GET', '/users/me/data');
}

/** The open request to delete the account, or null without one. */
export async function fetchDeletionRequest(): Promise<DeletionRequest | null> {
  try {
    return await request<DeletionRequest>('GET', '/users/me/deletion-request');
  } catch (caught) {
    const noRequest = caught instanceof ApiError && caught.status === NOT_FOUND;
    if (noRequest) return null;
    throw caught;
  }
}

/** Asks to delete the account; asking again returns the first request. */
export function requestDeletion(): Promise<DeletionRequest> {
  return request<DeletionRequest>('POST', '/users/me/deletion-request');
}

export function withdrawDeletionRequest(): Promise<void> {
  return request<void>('DELETE', '/users/me/deletion-request');
}

/** Administrator: the requests to delete an account, the oldest first. */
export async function fetchDeletionRequests(): Promise<OpenDeletionRequest[]> {
  const list = await request<components['schemas']['DeletionRequestListDto']>('GET', '/admin/deletion-requests');
  return list.items;
}

/** Administrator: handles the request by anonymising the account. */
export function anonymiseAccount(userId: number): Promise<void> {
  return request<void>('POST', `/admin/users/${userId}/anonymise`);
}

/** Operator or administrator: the callbacks to make, the oldest first. */
export async function fetchCallbacks(): Promise<Callback[]> {
  const list = await request<components['schemas']['CallbackListDto']>('GET', '/help-requests/callbacks');
  return list.items;
}

export function markCallbackHandled(id: number): Promise<void> {
  return request<void>('POST', `/help-requests/${id}/handled`);
}
