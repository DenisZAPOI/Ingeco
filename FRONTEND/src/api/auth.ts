import type { components } from '../types/api';
import { request, storedSession } from './client';

export type User = components['schemas']['UserDto'];
export type Role = User['role'];
export type RegisterData = components['schemas']['RegisterBody'];
export type RegistrationCode = components['schemas']['RegistrationCodeDto'];
export type ConfirmRegistrationData = components['schemas']['ConfirmRegistrationBody'];
export type LoginData = components['schemas']['LoginBody'];
export type ActivateData = components['schemas']['ActivateBody'];
export type PasswordResetData = components['schemas']['PasswordResetBody'];
export type PasswordResetCode = components['schemas']['PasswordResetCodeDto'];

/** First step: the API sends a code by SMS. Nothing is created yet. */
export function askRegistrationCode(data: RegisterData): Promise<RegistrationCode> {
  return request<RegistrationCode>('POST', '/auth/register', data);
}

/** Second step: the code creates the account and opens the session. */
export function confirmRegistration(data: ConfirmRegistrationData): Promise<User> {
  return request<User>('POST', '/auth/register/confirm', data);
}

export function login(data: LoginData): Promise<User> {
  return request<User>('POST', '/auth/login', data);
}

export function activate(data: ActivateData): Promise<User> {
  return request<User>('POST', '/auth/activate', data);
}

/** Forgotten password: the API sends a code by SMS, to type in activate().
 *  Same answer whether the number has an account or not. */
export function askPasswordResetCode(data: PasswordResetData): Promise<PasswordResetCode> {
  return request<PasswordResetCode>('POST', '/auth/password-reset', data);
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
