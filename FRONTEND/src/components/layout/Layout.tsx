import { useEffect, useRef, useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';

import { DriverLocationProvider } from '../../context/DriverLocationProvider';
import { useOnline } from '../../hooks/useOnline';
import { useSession } from '../../hooks/useSession';
import { errorMessage } from '../../lib/errorMessage';
import { ABOUT_PATH } from '../../lib/paths';
import { ErrorAlert } from '../ui/ErrorAlert';
import { LogoMark } from '../ui/icons';

export function Layout() {
  const { user, status, error, retry, logout } = useSession();
  const online = useOnline();
  const wasOnline = useRef(online);
  const [logoutError, setLogoutError] = useState<string | null>(null);
  const { pathname } = useLocation();

  // A new page starts at its top: the router keeps the scroll of the previous
  // one, which hides the title of the next booking step.
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

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
          <LogoMark className="brand-mark" />
          En route pour l'emploi
        </Link>
        {user && (
          <button type="button" className="header-action" onClick={handleLogout}>
            Se déconnecter
          </button>
        )}
      </header>
      <main className="main">
        {/* On the green, between the header and the band: seen first, on every screen. */}
        <div className="layout-alerts">
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
        </div>
        {/* A driver's position is sent from every screen while they are available. */}
        <DriverLocationProvider>
          <Outlet />
        </DriverLocationProvider>
      </main>
      {/* Required on every screen by the cahier des charges (§14). Copied in index.html. */}
      <footer className="footer">
        Projet étudiant — démonstrateur · <Link to={ABOUT_PATH}>À propos</Link>
      </footer>
    </>
  );
}
