import { useState } from 'react';
import { Link, Outlet } from 'react-router-dom';

import { useSession } from '../../hooks/useSession';
import { errorMessage } from '../../lib/errorMessage';
import { RequestState } from '../ui/RequestState';

export function Layout() {
  const { user, status, error, retry, logout } = useSession();
  const [logoutError, setLogoutError] = useState<string | null>(null);

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
        {logoutError && user && (
          <p role="alert" className="alert alert-error">
            {logoutError}
          </p>
        )}
        {/* Nothing is shown before knowing whether someone is logged in on this phone. */}
        <RequestState loading={status === 'loading'} error={status === 'error' ? error : null} onRetry={retry}>
          <Outlet />
        </RequestState>
      </main>
    </>
  );
}
