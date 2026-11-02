import type { components } from '../types/api';
import { request } from './client';

export type Availability = components['schemas']['AvailabilityDto'];
export type OfferList = components['schemas']['OfferListDto'];
export type Offer = components['schemas']['OfferDto'];
export type OfferType = components['schemas']['OffersQuery']['type'];
export type Position = components['schemas']['LocationBody'];

export function setAvailability(isAvailable: boolean): Promise<Availability> {
  return request<Availability>('PUT', '/drivers/me/availability', { isAvailable });
}

/** Last position of an online driver. 409 if the API sees them offline. */
export function sendLocation(position: Position): Promise<void> {
  return request<void>('PUT', '/drivers/me/location', position);
}

export function fetchOffers(type: OfferType): Promise<OfferList> {
  return request<OfferList>('GET', `/drivers/me/ride-offers?type=${type}`);
}

export type Earnings = components['schemas']['EarningsDto'];

/** Completed rides from `from` to `to` ('YYYY-MM-DD', Guyana days, both included), per day. */
export function fetchEarnings(from: string, to: string): Promise<Earnings> {
  return request<Earnings>('GET', `/drivers/me/earnings?${new URLSearchParams({ from, to })}`);
}
