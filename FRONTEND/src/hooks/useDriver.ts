import { useCallback } from 'react';

import { fetchOffers, setAvailability, type OfferType } from '../api/drivers';
import { driveRide, type RideAction } from '../api/rides';
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
