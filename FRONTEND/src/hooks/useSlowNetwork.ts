import { useEffect, useState } from 'react';

// On 2G a call usually answers within 3 s. Beyond that, the user must know
// the app is still working, or they tap again or close it.
const SLOW_NETWORK_DELAY_MS = 3_000;

/** True once `waiting` has lasted longer than a normal 2G call. */
export function useSlowNetwork(waiting: boolean): boolean {
  const [slow, setSlow] = useState(false);

  useEffect(() => {
    if (!waiting) return;
    const timer = setTimeout(() => setSlow(true), SLOW_NETWORK_DELAY_MS);
    return () => {
      clearTimeout(timer);
      setSlow(false);
    };
  }, [waiting]);

  return waiting && slow;
}
