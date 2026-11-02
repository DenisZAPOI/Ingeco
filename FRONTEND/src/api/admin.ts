import type { components } from '../types/api';
import { apiUrl, request } from './client';

export type Account = components['schemas']['AccountDto'];
export type AccountList = components['schemas']['AccountListDto'];
export type AccountRole = Account['role'];
export type AccountStatus = Account['status'];
export type NewAccount = components['schemas']['CreateAccountBody'];
export type StaffRole = NewAccount['role'];
export type CreatedAccount = components['schemas']['CreatedAccountDto'];
/** Only the fields sent are changed. */
export type AccountChanges = Partial<components['schemas']['UpdateAccountBody']>;
export type VehicleData = components['schemas']['VehicleBody'];
export type ActivationCode = components['schemas']['ActivationCodeDto'];

export type AccountFilters = {
  search: string | null;
  role: AccountRole | null;
  status: AccountStatus | null;
};

/** A page of accounts, the newest first. `cursor`: nextCursor of the previous page. */
export function fetchAccounts(filters: AccountFilters, cursor: string | null): Promise<AccountList> {
  const query = new URLSearchParams();
  if (filters.search) query.set('search', filters.search);
  if (filters.role) query.set('role', filters.role);
  if (filters.status) query.set('status', filters.status);
  if (cursor) query.set('cursor', cursor);
  return request<AccountList>('GET', `/admin/users?${query}`);
}

export function fetchAccount(id: number): Promise<Account> {
  return request<Account>('GET', `/admin/users/${id}`);
}

/** The answer carries the activation code, shown once. */
export function createAccount(account: NewAccount): Promise<CreatedAccount> {
  return request<CreatedAccount>('POST', '/admin/users', account);
}

export function updateAccount(id: number, changes: AccountChanges): Promise<Account> {
  return request<Account>('PATCH', `/admin/users/${id}`, changes);
}

/** A JPEG already reduced by the browser (lib/photo.ts). */
export function savePhoto(id: number, imageBase64: string): Promise<Account> {
  return request<Account>('PUT', `/admin/users/${id}/photo`, { imageBase64 });
}

/** Replaces the previous code. */
export function newActivationCode(id: number): Promise<ActivationCode> {
  return request<ActivationCode>('POST', `/admin/users/${id}/activation-code`);
}

/** Address of the driver's photo, with its date: a new photo is not hidden by the cache. */
export function photoUrl(account: Account): string | null {
  if (!account.photoUpdatedAt) return null;
  return apiUrl(`/admin/users/${account.id}/photo?v=${encodeURIComponent(account.photoUpdatedAt)}`);
}
