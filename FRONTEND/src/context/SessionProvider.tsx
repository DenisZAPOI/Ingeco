import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';

import { fetchMe, logout as logoutRequest, type User } from '../api/auth';
import { ApiError, onSessionExpired } from '../api/client';
import { errorMessage } from '../lib/errorMessage';
import { SessionContext, type Session, type SessionStatus } from './sessionContext';

const UNAUTHORIZED = 401;

/** Reads the session once at startup, then keeps the logged-in account for every screen. */
export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<SessionStatus>('loading');
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    // The session could not be renewed: back to the visitor screens.
    onSessionExpired(() => setUser(null));
  }, []);

  useEffect(() => {
    let cancelled = false;
    fetchMe()
      .then((me) => {
        if (cancelled) return;
        setUser(me);
        setStatus('ready');
      })
      .catch((caught: unknown) => {
        if (cancelled) return;
        // 401: simply nobody logged in on this phone.
        if (caught instanceof ApiError && caught.status === UNAUTHORIZED) {
          setUser(null);
          setStatus('ready');
          return;
        }
        setError(errorMessage(caught));
        setStatus('error');
      });
    return () => {
      cancelled = true;
    };
  }, [attempt]);

  const retry = useCallback(() => {
    setStatus('loading');
    setError(null);
    setAttempt((count) => count + 1);
  }, []);

  const logout = useCallback(async () => {
    // Only the API can erase the HttpOnly cookies: if the call fails, the
    // account must stay visible, or it would come back at the next opening
    // while the user (on a shared phone) thinks they are logged out.
    await logoutRequest();
    setUser(null);
  }, []);

  const session = useMemo<Session>(
    () => ({ user, status, error, retry, setUser, logout }),
    [user, status, error, retry, logout],
  );

  return <SessionContext.Provider value={session}>{children}</SessionContext.Provider>;
}
