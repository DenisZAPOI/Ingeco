import { useCallback, useEffect, useRef, useState } from 'react';

import { errorMessage } from '../lib/errorMessage';

/** Loads data for a screen: loading state, error message, retry, quiet reload.
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

  // The `load` of the screen as it is now: an answer to an older one (another
  // ride since) must not replace what is shown.
  const currentLoad = useRef(load);
  useEffect(() => {
    currentLoad.current = load;
  }, [load]);

  /** Reads again in the background, the screen kept as it is: for a change
   *  announced by the server (real time), that the user did not ask for.
   *  Unlike retry, no loading message; a failure changes nothing on screen,
   *  the "Actualiser" button is still there. */
  const reloadQuietly = useCallback(() => {
    load()
      .then((result) => {
        if (currentLoad.current !== load) return;
        setData(result);
        setError(null);
      })
      .catch(keepWhatIsShown);
  }, [load]);

  return { data, setData, loading, error, retry, reloadQuietly };
}

function keepWhatIsShown(): void {
  // Nothing to do: the previous state stays on screen.
}
