import type { components } from '../types/api';
import { request } from './client';

export type Commune = components['schemas']['CommuneDto'];
export type Place = components['schemas']['PlaceDto'];

export async function fetchCommunes(): Promise<Commune[]> {
  return (await request<components['schemas']['CommuneListDto']>('GET', '/communes')).items;
}

export async function searchPlaces(search: string, communeId: number): Promise<Place[]> {
  const query = new URLSearchParams({ search, communeId: String(communeId) });
  return (await request<components['schemas']['PlaceListDto']>('GET', `/places?${query}`)).items;
}
