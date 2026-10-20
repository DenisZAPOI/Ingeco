import { Navigate, Outlet } from 'react-router-dom';

import { useSession } from '../hooks/useSession';

// Navigation comfort only: these redirections protect nothing, the API checks
// every request.

/** Pages for a logged-in user. A visitor is sent to the login page. */
export function LoggedInRoutes() {
  const { user } = useSession();
  return user ? <Outlet /> : <Navigate to="/connexion" replace />;
}

/** Login, registration, activation. Once logged in, back to the home page. */
export function VisitorRoutes() {
  const { user } = useSession();
  return user ? <Navigate to="/" replace /> : <Outlet />;
}
