import { useEffect, useRef, useState } from 'react';
import { Link, Outlet } from 'react-router-dom';

import { useOnline } from '../../hooks/useOnline';
import { useSession } from '../../hooks/useSession';
import { errorMessage } from '../../lib/errorMessage';
import { ErrorAlert } from '../ui/ErrorAlert';

export function Layout() {
  const { user, status, error, retry, logout } = useSession();
  const online = useOnline();
  const wasOnline = useRef(online);
  const [logoutError, setLogoutError] = useState<string | null>(null);

  // The session could not be read for lack of network: read it again as soon
  // as the network is back, without waiting for the user to tap "Réessayer".
  // Only on that return: an API that fails while the network is fine would
  // otherwise be called again and again.
  useEffect(() => {
    if (online && !wasOnline.current && status === 'error') retry();
    wasOnline.current = online;
  }, [online, status, retry]);

  async function handleLogout() {
    setLogoutError(null);
    try {
      await logout();
    } catch (caught) {
      setLogoutError(`Déconnexion impossible. ${errorMessage(caught)}`);
    }
  }

  return (
    <>
      <header className="header">
        <Link to="/" className="brand">
          En route pour l'emploi
        </Link>
        {user && (
          <button type="button" className="header-action" onClick={handleLogout}>
            Se déconnecter
          </button>
        )}
      </header>
      <main className="main">
        {!online && (
          <p role="status" className="alert alert-info">
            Pas de connexion internet. L'application reprendra dès le retour du réseau.
          </p>
        )}
        {logoutError && user && (
          <p role="alert" className="alert alert-error">
            {logoutError}
          </p>
        )}
        {/* Screens are not held back by the session read (see SessionProvider):
            only its failure is shown, the offline message already covers a lost network. */}
        {online && status === 'error' && error && <ErrorAlert message={error} onRetry={retry} />}
        <Outlet />
      </main>
    </>
  );
}
