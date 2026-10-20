import { Navigate, Outlet } from 'react-router-dom';

import { LoadingMessage } from '../components/ui/LoadingMessage';
import { useSession } from '../hooks/useSession';

// Navigation comfort only: these redirections protect nothing, the API checks
// every request.

/** Pages for a logged-in user. A visitor is sent to the login page. */
export function LoggedInRoutes() {
  const { user, status } = useSession();
  if (user) {
    return <Outlet />;
  }
  // Not known yet: a reload of /profil must not send a logged-in user to the
  // login page. A failure is shown by the Layout, with its "Réessayer".
  if (status !== 'ready') {
    return status === 'loading' ? <LoadingMessage /> : null;
  }
  return <Navigate to="/connexion" replace />;
}

/** Login, registration, activation. Once logged in, back to the home page.
 *  Shown while the session is read: most people who open them are visitors. */
export function VisitorRoutes() {
  const { user } = useSession();
  return user ? <Navigate to="/" replace /> : <Outlet />;
}
