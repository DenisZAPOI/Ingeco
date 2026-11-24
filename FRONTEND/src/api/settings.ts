import type { components } from '../types/api';
import { request } from './client';

export type Week = components['schemas']['WeekDto'];
export type DayHours = components['schemas']['DayHoursDto'];
export type WeekBody = components['schemas']['WeekBody'];
export type ZoneList = components['schemas']['ZoneListDto'];
export type Zone = components['schemas']['ZoneDto'];
export type Tariff = components['schemas']['TariffDto'];
export type TariffBody = components['schemas']['TariffBody'];

/** The 7 days, Monday first, in local time of Cayenne; null: closed that day. */
export function fetchServiceHours(): Promise<Week> {
  return request<Week>('GET', '/admin/service-hours');
}

/** Replaces the whole week. */
export function saveServiceHours(week: WeekBody): Promise<Week> {
  return request<Week>('PUT', '/admin/service-hours', week);
}

/** The 22 communes, by name, served or not. */
export function fetchZones(): Promise<ZoneList> {
  return request<ZoneList>('GET', '/admin/zones');
}

/** These communes receive rides from now on, the others no longer do. */
export function saveZones(servedCommuneIds: number[]): Promise<ZoneList> {
  return request<ZoneList>('PUT', '/admin/zones', { servedCommuneIds });
}

export function fetchTariff(): Promise<Tariff> {
  return request<Tariff>('GET', '/admin/tariff');
}

/** A new version of the tariff, for the next bookings. */
export function createTariff(tariff: TariffBody): Promise<Tariff> {
  return request<Tariff>('POST', '/admin/tariff', tariff);
}
