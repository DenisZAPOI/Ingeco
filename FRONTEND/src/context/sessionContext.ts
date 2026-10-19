import { createContext } from 'react';

import type { User } from '../api/auth';

export type SessionStatus = 'loading' | 'ready' | 'error';

export type Session = {
  /** The logged-in account, or null for a visitor. */
  user: User | null;
  status: SessionStatus;
  /** Message when the session could not be read (network down at startup). */
  error: string | null;
  retry: () => void;
  /** After login, registration, activation or a profile change. */
  setUser: (user: User | null) => void;
  /** Rejects when the API cannot be reached: the user is then still logged in. */
  logout: () => Promise<void>;
};

export const SessionContext = createContext<Session | null>(null);
