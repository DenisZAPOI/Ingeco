import { useCallback } from 'react';

import { bookRide, estimateRide, fetchRide, payRide, type Booking, type Ride, type Stop } from '../api/rides';
import { useRequest } from './useRequest';
import { useSubmit } from './useSubmit';

export function useEstimate(pickup: Stop, dropoff: Stop) {
  return useRequest(useCallback(() => estimateRide(pickup, dropoff), [pickup, dropoff]));
}

/** `known`: the ride handed over by the previous screen, shown without a call. */
export function useRide(id: number, known: Ride | null) {
  return useRequest(useCallback(() => fetchRide(id), [id]), known);
}

export function useBookRide() {
  return useSubmit(useCallback((booking: Booking) => bookRide(booking), []));
}

export function usePayRide() {
  return useSubmit(useCallback((id: number) => payRide(id), []));
}
