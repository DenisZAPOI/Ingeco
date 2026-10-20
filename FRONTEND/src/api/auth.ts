import type { components } from '../types/api';
import { request, storedSession } from './client';

export type User = components['schemas']['UserDto'];
export type Role = User['role'];
export type RegisterData = components['schemas']['RegisterBody'];
export type LoginData = components['schemas']['LoginBody'];
export type ActivateData = components['schemas']['ActivateBody'];

export function register(data: RegisterData): Promise<User> {
  return request<User>('POST', '/auth/register', data);
}

export function login(data: LoginData): Promise<User> {
  return request<User>('POST', '/auth/login', data);
}

export function activate(data: ActivateData): Promise<User> {
  return request<User>('POST', '/auth/activate', data);
}

export function logout(): Promise<void> {
  return request<void>('POST', '/auth/logout');
}

export function fetchMe(): Promise<User> {
  return request<User>('GET', '/auth/me');
}

/** The logged-in account, or null for a visitor, in as few calls as the
 *  cookies allow: none for a visitor, one otherwise (the renewal returns the
 *  account too). Rejects with a 401 when the session has ended. */
export async function fetchSession(): Promise<User | null> {
  switch (storedSession()) {
    case 'none':
      return null;
    case 'expired':
      return request<User>('POST', '/auth/refresh');
    case 'active':
      return fetchMe();
  }
}
