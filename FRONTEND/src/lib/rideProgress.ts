import type { RideStatus } from '../api/rides';

/** The steps of a trip shown to the rider, in order. A cancelled or expired
 *  trip leaves this path: it shows its status only. */
export const RIDE_PROGRESS_STEPS = ['sent', 'driverFound', 'onTheWay', 'arrived'] as const;

export type RideProgressStep = (typeof RIDE_PROGRESS_STEPS)[number];

// How many steps each status has reached. Not listed: off the path.
const STEPS_REACHED: Partial<Record<RideStatus, number>> = {
  pending: 1,
  accepted: 2,
  in_progress: 3,
  completed: 4,
};

/** The number of steps reached by a trip, or null when it is off the path
 *  (not paid yet, cancelled, expired): then no bar is shown. */
export function rideStepsReached(status: RideStatus): number | null {
  return STEPS_REACHED[status] ?? null;
}
