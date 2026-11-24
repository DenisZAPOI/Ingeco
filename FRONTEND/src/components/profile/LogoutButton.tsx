import { useState } from 'react';

import { useSession } from '../../hooks/useSession';
import { t } from '../../i18n';
import { errorMessage } from '../../lib/errorMessage';

/** « Se déconnecter » at the bottom of the profile: where a rider or a
 *  driver finds it, their header keeping only the name of the application. */
export function LogoutButton() {
  const { logout } = useSession();
  const [error, setError] = useState<string | null>(null);
  const [leaving, setLeaving] = useState(false);

  async function leave() {
    setError(null);
    setLeaving(true);
    try {
      await logout();
    } catch (caught) {
      setError(t('common.logoutFailed', { reason: errorMessage(caught) }));
      setLeaving(false);
    }
  }

  return (
    <div className="stack">
      {error && (
        <p role="alert" className="alert alert-error">
          {error}
        </p>
      )}
      <button type="button" className="button button-block button-secondary" onClick={leave} disabled={leaving}>
        {leaving ? t('common.sending') : t('common.logout')}
      </button>
    </div>
  );
}
