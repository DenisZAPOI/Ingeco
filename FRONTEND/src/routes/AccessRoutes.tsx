import { Navigate, Outlet, useLocation } from 'react-router-dom';

import { LoadingMessage } from '../components/ui/LoadingMessage';
import { useSession } from '../hooks/useSession';
import { LOGIN_PATH, returnPathFromState } from '../lib/paths';

// Navigation comfort only: these redirections protect nothing, the API checks
// every request.

/** Pages for a logged-in user. A visitor is sent to the login page. */
export function LoggedInRoutes() {
  const { user, hint, status } = useSession();
  const location = useLocation();
  // Logged in last time on this phone: the page is shown and starts its own
  // calls at once, while the API confirms the session. On 2G, waiting for
  // /auth/me first costs a round trip before every logged-in page.
  if (user || (hint && status === 'loading')) {
    return <Outlet />;
  }
  // Not known yet: a reload of /profil must not send a logged-in user to the
  // login page. A failure is shown by the Layout, with its "Réessayer".
  if (status !== 'ready') {
    return status === 'loading' ? <LoadingMessage /> : null;
  }
  // Once logged in, back to the page asked for ("Comment y aller ?" on a job
  // offer leads to the booking): handed over in the router state.
  return <Navigate to={LOGIN_PATH} replace state={{ returnTo: location.pathname + location.search }} />;
}

/** Login, registration, activation. Once logged in, back to the page the
 *  visitor was sent from, or to the home page. Shown while the session is
 *  read: most people who open them are visitors. */
export function VisitorRoutes() {
  const { user } = useSession();
  const location = useLocation();
  return user ? <Navigate to={returnPathFromState(location.state) ?? '/'} replace /> : <Outlet />;
}
