import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';

import { fetchSession, logout as logoutRequest, type User } from '../api/auth';
import { ApiError, onSessionExpired } from '../api/client';
import { errorMessage } from '../lib/errorMessage';
import { readSessionHint, saveSessionHint, type SessionHint } from '../lib/sessionHint';
import { SessionContext, type Session, type SessionStatus } from './sessionContext';

const UNAUTHORIZED = 401;

/** Reads the session once at startup, then keeps the logged-in account for every screen.
 *  Screens are not held back meanwhile: they draw from the hint left by the
 *  last session, and the API confirms or corrects it. */
export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<User | null>(null);
  const [hint] = useState<SessionHint | null>(readSessionHint);
  const [status, setStatus] = useState<SessionStatus>('loading');
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  // A visitor can log in before the startup read answers (it can take seconds
  // on 2G): that answer is then out of date and must not undo the login.
  const accountSetByScreen = useRef(false);

  // Every change of account goes through here, so the hint always matches.
  const applyUser = useCallback((next: User | null) => {
    saveSessionHint(next);
    setUserState(next);
    setError(null);
    setStatus('ready');
  }, []);

  const setUser = useCallback(
    (next: User | null) => {
      accountSetByScreen.current = true;
      applyUser(next);
    },
    [applyUser],
  );

  useEffect(() => {
    // The session could not be renewed: back to the visitor screens.
    onSessionExpired(() => setUser(null));
  }, [setUser]);

  useEffect(() => {
    let cancelled = false;
    const isOutdated = () => cancelled || accountSetByScreen.current;
    fetchSession()
      .then((me) => {
        if (!isOutdated()) applyUser(me);
      })
      .catch((caught: unknown) => {
        if (isOutdated()) return;
        // 401: simply nobody logged in on this phone.
        if (caught instanceof ApiError && caught.status === UNAUTHORIZED) {
          applyUser(null);
          return;
        }
        setError(errorMessage(caught));
        setStatus('error');
      });
    return () => {
      cancelled = true;
    };
  }, [attempt, applyUser]);

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
  }, [setUser]);

  const session = useMemo<Session>(
    () => ({ user, status, hint: status === 'ready' ? null : hint, error, retry, setUser, logout }),
    [user, status, hint, error, retry, setUser, logout],
  );

  return <SessionContext.Provider value={session}>{children}</SessionContext.Provider>;
}
