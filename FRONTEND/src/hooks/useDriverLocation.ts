import { useContext } from 'react';

import { DriverLocationContext, type LocationStatus } from '../context/driverLocationContext';

export function useDriverLocation(): LocationStatus {
  return useContext(DriverLocationContext);
}
