import { useCallback } from 'react';

import { fetchEarnings, fetchOffers, setAvailability, type OfferType } from '../api/drivers';
import { driveRide, type RideAction } from '../api/rides';
import { periodBounds, type EarningsPeriod } from '../lib/earnings';
import { useRequest } from './useRequest';
import { useSubmit } from './useSubmit';

export function useSetAvailability() {
  return useSubmit(useCallback((available: boolean) => setAvailability(available), []));
}

export function useOffers(type: OfferType) {
  return useRequest(useCallback(() => fetchOffers(type), [type]));
}

export function useDriveRide(id: number) {
  return useSubmit(useCallback((action: RideAction) => driveRide(id, action), [id]));
}

/** Earnings of today, this week or this month (Guyana days). */
export function useEarnings(period: EarningsPeriod) {
  return useRequest(
    useCallback(() => {
      const { from, to } = periodBounds(period);
      return fetchEarnings(from, to);
    }, [period]),
  );
}
