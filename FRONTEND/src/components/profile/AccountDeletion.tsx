import { useState } from 'react';

import { fetchDeletionRequest, requestDeletion, withdrawDeletionRequest } from '../../api/privacy';
import { useRequest } from '../../hooks/useRequest';
import { useSubmit } from '../../hooks/useSubmit';
import { t } from '../../i18n';
import { formatDateTime } from '../../lib/format';
import { RequestState } from '../ui/RequestState';

/** « Supprimer mon compte » (RGPD art. 17, audit R3): a request an
 *  administrator handles, that the person may withdraw until then. */
export function AccountDeletion() {
  const current = useRequest(fetchDeletionRequest);
  const [confirming, setConfirming] = useState(false);
  const ask = useSubmit(requestDeletion);
  const withdraw = useSubmit(withdrawDeletionRequest);
  const requestedAt = current.data?.requestedAt ?? null;

  async function confirmRequest() {
    const sent = await ask.submit(undefined);
    if (sent !== null) {
      current.setData(sent);
      setConfirming(false);
    }
  }

  async function withdrawRequest() {
    // `undefined` on success (204): null means it failed.
    const result = await withdraw.submit(undefined);
    if (result !== null) current.setData(null);
  }

  return (
    <>
      <h2>{t('deletion.title')}</h2>
      <RequestState loading={current.loading} error={current.error} onRetry={current.retry}>
        {requestedAt ? (
          <>
            <p className="alert alert-info">{t('deletion.pending', { date: formatDateTime(requestedAt) })}</p>
            {withdraw.error && <p className="alert alert-error">{withdraw.error}</p>}
            <button type="button" className="button button-block button-secondary" onClick={withdrawRequest} disabled={withdraw.submitting}>
              {t('deletion.withdraw')}
            </button>
          </>
        ) : confirming ? (
          <>
            <p className="alert alert-info">{t('deletion.warning')}</p>
            {ask.error && <p className="alert alert-error">{ask.error}</p>}
            <button type="button" className="button button-block" onClick={confirmRequest} disabled={ask.submitting}>
              {t('deletion.confirm')}
            </button>
            <button type="button" className="button button-block button-secondary" onClick={() => setConfirming(false)}>
              {t('deletion.cancel')}
            </button>
          </>
        ) : (
          <>
            <p>{t('deletion.lead')}</p>
            <button type="button" className="button button-block button-secondary" onClick={() => setConfirming(true)}>
              {t('deletion.ask')}
            </button>
          </>
        )}
      </RequestState>
    </>
  );
}
