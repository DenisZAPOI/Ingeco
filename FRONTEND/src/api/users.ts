import type { components } from '../types/api';
import type { User } from './auth';
import { request } from './client';

// Only the fields sent are changed: the generated type lists them all.
export type ProfileChanges = Partial<components['schemas']['UpdateProfileBody']>;

export function updateProfile(changes: ProfileChanges): Promise<User> {
  return request<User>('PATCH', '/users/me', changes);
}
