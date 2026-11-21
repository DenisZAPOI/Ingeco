import { useEffect } from 'react';

import { followOffers, followRide } from '../api/realtime';

/** While the screen is shown, `onChange` runs when the ride changes (and at
 *  every reconnection). `onChange` must be stable: useRequest's reloadQuietly. */
export function useRideUpdates(rideId: number, onChange: () => void) {
  useEffect(() => followRide(rideId, onChange), [rideId, onChange]);
}

/** While the driver's list of rides to take is shown, `onChange` runs when it changes. */
export function useOfferUpdates(onChange: () => void) {
  useEffect(() => followOffers(onChange), [onChange]);
}
