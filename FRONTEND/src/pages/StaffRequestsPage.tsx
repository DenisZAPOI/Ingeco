import { useState } from 'react';

import {
  anonymiseAccount,
  fetchCallbacks,
  fetchDeletionRequests,
  markCallbackHandled,
  type Callback,
  type OpenDeletionRequest,
} from '../api/privacy';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { RequestState } from '../components/ui/RequestState';
import { useRequest } from '../hooks/useRequest';
import { useSession } from '../hooks/useSession';
import { useSubmit } from '../hooks/useSubmit';
import { t } from '../i18n';
import { formatDateTime } from '../lib/format';
import { formatPhone } from '../lib/phone';

/** « Demandes » : the callbacks to make (operator, administrator) and the
 *  accounts to delete (administrator), the oldest first (audit RGPD R3, R10). */
export function StaffRequestsPage() {
  const { user } = useSession();
  const isAdmin = user?.role === 'admin';

  return (
    <section>
      <PageHero title={t('requests.title')} />
      <PageSheet>
        <Callbacks />
        {isAdmin && <DeletionRequests />}
      </PageSheet>
    </section>
  );
}

function Callbacks() {
  const callbacks = useRequest(fetchCallbacks);
  const items = callbacks.data ?? [];
  return (
    <>
      <h2>{t('requests.callbacksTitle')}</h2>
      <RequestState loading={callbacks.loading} error={callbacks.error} onRetry={callbacks.retry}>
        {items.length === 0 ? (
          <p>{t('requests.noCallback')}</p>
        ) : (
          <ul className="ride-list">
            {items.map((callback) => (
              <li key={callback.id}>
                <CallbackItem callback={callback} onDone={callbacks.retry} />
              </li>
            ))}
          </ul>
        )}
      </RequestState>
    </>
  );
}

function CallbackItem({ callback, onDone }: { callback: Callback; onDone: () => void }) {
  const handle = useSubmit(markCallbackHandled);
  const who = callback.hasAccount ? t('requests.withAccount') : t('requests.withoutAccount');

  async function done() {
    const result = await handle.submit(callback.id);
    // `undefined` on success (204): null means it failed.
    if (result !== null) onDone();
  }

  return (
    <div className="panel">
      <p>
        {callback.phone ? <a href={`tel:${callback.phone}`}>{formatPhone(callback.phone)}</a> : t('myData.none')}
        <br />
        <span className="note">{t('requests.askedOn', { date: formatDateTime(callback.createdAt), who })}</span>
      </p>
      {handle.error && <p className="alert alert-error">{handle.error}</p>}
      <button type="button" className="button button-block button-secondary" onClick={done} disabled={handle.submitting}>
        {t('requests.calledBack')}
      </button>
    </div>
  );
}

function DeletionRequests() {
  const requests = useRequest(fetchDeletionRequests);
  const items = requests.data ?? [];
  return (
    <>
      <h2>{t('requests.deletionsTitle')}</h2>
      <p className="note">{t('requests.deletionsLead')}</p>
      <RequestState loading={requests.loading} error={requests.error} onRetry={requests.retry}>
        {items.length === 0 ? (
          <p>{t('requests.noDeletion')}</p>
        ) : (
          <ul className="ride-list">
            {items.map((request) => (
              <li key={request.userId}>
                <DeletionItem request={request} onDone={requests.retry} />
              </li>
            ))}
          </ul>
        )}
      </RequestState>
    </>
  );
}

function DeletionItem({ request, onDone }: { request: OpenDeletionRequest; onDone: () => void }) {
  const [confirming, setConfirming] = useState(false);
  const anonymise = useSubmit(anonymiseAccount);
  const name = `${request.firstName} ${request.lastName}`;

  async function confirm() {
    const result = await anonymise.submit(request.userId);
    if (result !== null) onDone();
  }

  return (
    <div className="panel">
      <p>
        <strong>{name}</strong> · {formatPhone(request.phone)}
        <br />
        <span className="note">{t('requests.deletionAskedOn', { date: formatDateTime(request.requestedAt) })}</span>
      </p>
      {anonymise.error && <p className="alert alert-error">{anonymise.error}</p>}
      {confirming ? (
        <>
          <p className="alert alert-info">{t('requests.anonymiseWarning', { name })}</p>
          <button type="button" className="button button-block" onClick={confirm} disabled={anonymise.submitting}>
            {t('requests.anonymiseConfirm')}
          </button>
          <button type="button" className="button button-block button-secondary" onClick={() => setConfirming(false)}>
            {t('requests.cancel')}
          </button>
        </>
      ) : (
        <button type="button" className="button button-block button-secondary" onClick={() => setConfirming(true)}>
          {t('requests.anonymise')}
        </button>
      )}
    </div>
  );
}
