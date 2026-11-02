import { useCallback, useEffect, useState } from 'react';

import { errorMessage } from '../lib/errorMessage';

/** Loads data for a screen: loading state, error message, retry.
 *
 *  `known` is a value already in hand (passed by the previous screen, or
 *  stored on the phone): it is shown at once. With `refresh`, the call still
 *  goes out to confirm it; without, no call at all. `load` must be stable
 *  (useCallback): a new function loads again. */
export function useRequest<T>(load: () => Promise<T>, known: T | null = null, refresh = false) {
  const [data, setData] = useState<T | null>(known);
  const [loading, setLoading] = useState(known === null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const skip = known !== null && !refresh && attempt === 0;

  useEffect(() => {
    if (skip) return;
    let cancelled = false;
    load()
      .then((result) => {
        if (!cancelled) {
          setData(result);
          setError(null);
        }
      })
      .catch((caught: unknown) => {
        if (!cancelled) setError(errorMessage(caught));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [load, attempt, skip]);

  const retry = useCallback(() => {
    setLoading(true);
    setError(null);
    setAttempt((count) => count + 1);
  }, []);

  return { data, setData, loading, error, retry };
}
