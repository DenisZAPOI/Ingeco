import type { components } from '../types/api';
import { request } from './client';

export type HelpService = components['schemas']['HelpServiceDto'];
export type HelpCategory = HelpService['category'];
export type SpokenLanguage = HelpService['spokenLanguages'][number];

/** Every help service, at once: the phone filters them (lib/helpServices.ts). */
export async function fetchHelpServices(): Promise<HelpService[]> {
  return (await request<components['schemas']['HelpServiceListDto']>('GET', '/help-services')).items;
}

export function fetchHelpService(id: number): Promise<HelpService> {
  return request<HelpService>('GET', `/help-services/${id}`);
}
