import type { components } from '../types/api';
import { request } from './client';

export type PracticalGuide = components['schemas']['PracticalGuideDto'];

/** Every practical guide, at once (a handful): the phone filters them by need. */
export async function fetchPracticalGuides(): Promise<PracticalGuide[]> {
  return (await request<components['schemas']['PracticalGuideListDto']>('GET', '/practical-guides')).items;
}

export function fetchPracticalGuide(id: number): Promise<PracticalGuide> {
  return request<PracticalGuide>('GET', `/practical-guides/${id}`);
}
