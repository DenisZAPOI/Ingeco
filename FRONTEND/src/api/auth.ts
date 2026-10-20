import type { components } from '../types/api';
import { request } from './client';

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
