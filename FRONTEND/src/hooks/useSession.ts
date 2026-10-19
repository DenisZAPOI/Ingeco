import { useContext } from 'react';

import { SessionContext, type Session } from '../context/sessionContext';

export function useSession(): Session {
  const session = useContext(SessionContext);
  if (session === null) {
    throw new Error('useSession must be used inside <SessionProvider>.');
  }
  return session;
}
