import { createContext } from 'react';

import type { User } from '../api/auth';
import type { SessionHint } from '../lib/sessionHint';

export type SessionStatus = 'loading' | 'ready' | 'error';

export type Session = {
  /** The logged-in account, or null for a visitor. */
  user: User | null;
  status: SessionStatus;
  /** Who was logged in last time on this phone, until the API confirms `user`
   *  (see lib/sessionHint.ts). Null once the session is read. */
  hint: SessionHint | null;
  /** Message when the session could not be read (network down at startup). */
  error: string | null;
  retry: () => void;
  /** After login, registration, activation or a profile change. */
  setUser: (user: User | null) => void;
  /** Rejects when the API cannot be reached: the user is then still logged in. */
  logout: () => Promise<void>;
};

export const SessionContext = createContext<Session | null>(null);
