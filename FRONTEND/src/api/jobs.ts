import type { components } from '../types/api';
import { request } from './client';

export type JobOffer = components['schemas']['JobOfferDto'];
export type ContractType = JobOffer['contractType'];
export type Schedule = JobOffer['schedule'];

/** Every offer online, at once: the phone filters them (lib/jobs.ts). */
export async function fetchJobOffers(): Promise<JobOffer[]> {
  return (await request<components['schemas']['JobOfferListDto']>('GET', '/jobs')).items;
}

export function fetchJobOffer(id: number): Promise<JobOffer> {
  return request<JobOffer>('GET', `/jobs/${id}`);
}
