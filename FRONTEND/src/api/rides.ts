import type { components } from '../types/api';
import { request } from './client';

export type Ride = components['schemas']['RideDto'];
export type RideStatus = Ride['status'];
export type Purpose = Ride['purpose'];
export type Stop = components['schemas']['StopBody'];
export type Estimate = components['schemas']['EstimateDto'];
export type Booking = components['schemas']['BookRideBody'];

export function estimateRide(pickup: Stop, dropoff: Stop): Promise<Estimate> {
  return request<Estimate>('POST', '/rides/estimate', { pickup, dropoff });
}

/** Sent again with the same clientRequestId, returns the ride already booked. */
export function bookRide(booking: Booking): Promise<Ride> {
  return request<Ride>('POST', '/rides', booking);
}

export function fetchRide(id: number): Promise<Ride> {
  return request<Ride>('GET', `/rides/${id}`);
}

/** Simulated payment. Paying a ride already paid returns it unchanged. */
export function payRide(id: number): Promise<Ride> {
  return request<Ride>('POST', `/rides/${id}/payment`);
}
