import type { components } from '../types/api';
import { request } from './client';

export type Health = components['schemas']['HealthDto'];

export function fetchHealth(): Promise<Health> {
  return request<Health>('GET', '/health');
}
