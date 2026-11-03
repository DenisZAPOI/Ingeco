import type { RideStatus } from '../api/rides';
import { t } from '../i18n';

/** What the driver reads at the top of a ride ("course", their word). */
export function driverStatusHeadline(status: RideStatus): string {
  return t(`driverRide.headlines.${status}`);
}

/** Short state of a ride in the driver's lists. */
export function driverStatusLabel(status: RideStatus): string {
  return t(`driverRide.statuses.${status}`);
}
