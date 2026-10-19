import type { components } from '../types/api';
import { ApiError, request } from './client';

export type Health = components['schemas']['HealthDto'];

const SERVICE_UNAVAILABLE = 503;

export async function fetchHealth(): Promise<Health> {
  try {
    return await request<Health>('GET', '/health');
  } catch (error) {
    // A 503 still carries a HealthDto: the API answers but the database does
    // not. The page must show that state, not a generic error.
    if (error instanceof ApiError && error.status === SERVICE_UNAVAILABLE && isHealth(error.detail)) {
      return error.detail;
    }
    throw error;
  }
}

function isHealth(value: unknown): value is Health {
  return typeof value === 'object' && value !== null && 'status' in value && 'database' in value;
}
