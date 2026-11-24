import { describe, expect, it } from 'vitest';

import { RIDE_PROGRESS_STEPS, rideStepsReached } from './rideProgress';

describe('rideStepsReached', () => {
  it('counts the steps reached, one more for each status on the way', () => {
    expect(rideStepsReached('pending')).toBe(1);
    expect(rideStepsReached('accepted')).toBe(2);
    expect(rideStepsReached('in_progress')).toBe(3);
  });

  it('reaches every step once the trip is over', () => {
    expect(rideStepsReached('completed')).toBe(RIDE_PROGRESS_STEPS.length);
  });

  it('shows no bar for a trip off the path', () => {
    expect(rideStepsReached('awaiting_payment')).toBeNull();
    expect(rideStepsReached('cancelled')).toBeNull();
    expect(rideStepsReached('expired')).toBeNull();
  });
});
