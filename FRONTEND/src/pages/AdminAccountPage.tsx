import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';

import type { Account, ActivationCode } from '../api/admin';
import { ActivationCodePanel } from '../components/admin/ActivationCodePanel';
import { PhotoField } from '../components/admin/PhotoField';
import { VehicleFields } from '../components/admin/VehicleFields';
import { Form } from '../components/form/Form';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { ConfirmButton } from '../components/ui/ConfirmButton';
import { RequestState } from '../components/ui/RequestState';
import { useAccount, useNewActivationCode, useUpdateAccount } from '../hooks/useAdmin';
import { useSession } from '../hooks/useSession';
import { t } from '../i18n';
import { accountFromState, accountStatusLabel, activationFromState, roleLabel } from '../lib/accounts';
import { formatDateTime } from '../lib/format';
import { vehicleData, vehicleDraft } from '../lib/vehicle';
import { ADMIN_ACCOUNTS_PATH } from '../lib/paths';
import { formatPhone } from '../lib/phone';

/** UC51 to UC53 for one account: suspend or reactivate, priority, vehicle, photo, activation code. */
export function AdminAccountPage() {
  const id = Number(useParams().id);
  const location = useLocation();
  const navigate = useNavigate();
  const account = useAccount(id, accountFromState(location.state, id));
  // Kept on this screen only: the history forgets it at once, so Back and
  // Forward never show the code again.
  const [activation, setActivation] = useState<ActivationCode | null>(() => activationFromState(location.state));

  useEffect(() => {
    if (activationFromState(location.state)) {
      navigate(location.pathname, { replace: true, state: { account: accountFromState(location.state, id) } });
    }
  }, [location.state, location.pathname, navigate, id]);

  // The new state also replaces the one kept in the history: coming back
  // here later shows the account as it is now.
  function update(changed: Account) {
    account.setData(changed);
    navigate(location.pathname, { replace: true, state: { account: changed } });
  }

  return (
    <section>
      <PageHero title={account.data ? `${account.data.firstName} ${account.data.lastName}` : t('admin.accountTitle')} />
      <PageSheet>
        <RequestState loading={account.loading} error={account.error} onRetry={account.retry}>
          {account.data && (
            <AccountDetail
              account={account.data}
              activation={activation}
              onActivation={setActivation}
              onChange={update}
            />
          )}
        </RequestState>
        <Link to={ADMIN_ACCOUNTS_PATH} className="link-action">
          {t('admin.allAccounts')}
        </Link>
      </PageSheet>
    </section>
  );
}

type AccountDetailProps = {
  account: Account;
  activation: ActivationCode | null;
  onActivation: (activation: ActivationCode) => void;
  onChange: (account: Account) => void;
};

function AccountDetail({ account, activation, onActivation, onChange }: AccountDetailProps) {
  return (
    <>
      {activation && <ActivationCodePanel activation={activation} firstName={account.firstName} phone={account.phone} />}
      <Identity account={account} />
      {account.role === 'rider' && <Priority account={account} onChange={onChange} />}
      {account.role === 'driver' && (
        <>
          <h2>{t('admin.photo')}</h2>
          <p className="note">{t('admin.photoNote')}</p>
          <PhotoField account={account} onSaved={onChange} />
          <VehicleForm account={account} onChange={onChange} />
        </>
      )}
      <AccessActions account={account} onActivation={onActivation} onChange={onChange} />
    </>
  );
}

function Identity({ account }: { account: Account }) {
  return (
    <dl className="summary">
      <dt>{t('admin.role')}</dt>
      <dd>{roleLabel(account.role)}</dd>
      <dt>{t('admin.phone')}</dt>
      <dd>{formatPhone(account.phone)}</dd>
      {account.email && (
        <>
          <dt>{t('admin.email')}</dt>
          <dd>{account.email}</dd>
        </>
      )}
      <dt>{t('admin.status')}</dt>
      <dd>
        {accountStatusLabel(account.status)}
        {!account.isActivated && t('admin.notActivatedSuffix')}
      </dd>
      {account.role === 'rider' && account.needsAccessibleVehicle && (
        <>
          <dt>{t('admin.need')}</dt>
          <dd>{t('admin.accessibleNeed')}</dd>
        </>
      )}
      <dt>{t('admin.createdAt')}</dt>
      <dd>{formatDateTime(account.createdAt)}</dd>
    </dl>
  );
}

function Priority({ account, onChange }: { account: Account; onChange: (account: Account) => void }) {
  const { submit, submitting, error } = useUpdateAccount(account.id);

  async function toggle() {
    const changed = await submit({ isPriority: !account.isPriority });
    if (changed) onChange(changed);
  }

  return (
    <>
      <h2>{t('admin.priorityTitle')}</h2>
      <p>
        {account.isPriority ? t('admin.isPriority') : t('admin.isNotPriority')}{' '}
        <span className="note">{t('admin.priorityUse')}</span>
      </p>
      {error && (
        <p role="alert" className="alert alert-error">
          {error}
        </p>
      )}
      <button type="button" className="button button-block button-secondary" onClick={toggle} disabled={submitting}>
        {submitting ? t('common.sending') : account.isPriority ? t('admin.removePriority') : t('admin.setPriority')}
      </button>
    </>
  );
}

function VehicleForm({ account, onChange }: { account: Account; onChange: (account: Account) => void }) {
  const [draft, setDraft] = useState(vehicleDraft(account.vehicle));
  const [saved, setSaved] = useState(false);
  const { submit, submitting, error, errors } = useUpdateAccount(account.id);

  async function send() {
    setSaved(false);
    const changed = await submit({ vehicle: vehicleData(draft) });
    if (changed) {
      setSaved(true);
      onChange(changed);
    }
  }

  return (
    <>
      <h2>{t('admin.vehicle')}</h2>
      <Form
        onSubmit={send}
        submitLabel={t('admin.vehicleSubmit')}
        submitting={submitting}
        error={error}
        success={saved ? t('admin.vehicleSaved') : null}
      >
        <VehicleFields draft={draft} onChange={setDraft} errors={errors} prefix="vehicle" />
      </Form>
    </>
  );
}

type AccessActionsProps = {
  account: Account;
  onActivation: (activation: ActivationCode) => void;
  onChange: (account: Account) => void;
};

function AccessActions({ account, onActivation, onChange }: AccessActionsProps) {
  const { user } = useSession();
  const status = useUpdateAccount(account.id);
  const code = useNewActivationCode(account.id);
  // A new key closes the confirmation once the code is shown.
  const [codesIssued, setCodesIssued] = useState(0);
  const isMe = user?.id === account.id;

  async function setStatus(next: Account['status']) {
    const changed = await status.submit({ status: next });
    if (changed) onChange(changed);
  }

  async function issueCode() {
    const issued = await code.submit(undefined);
    if (issued) {
      onActivation(issued);
      setCodesIssued((count) => count + 1);
    }
  }

  return (
    <>
      <h2>{t('admin.access')}</h2>
      <ConfirmButton
        key={codesIssued}
        label={account.isActivated ? t('admin.newResetCode') : t('admin.newActivationCode')}
        question={t('admin.codeQuestion', { name: account.firstName })}
        details={
          <p>
            {t('admin.codeDetails')}
            {account.isActivated && t('admin.codeSmsWarning')}
          </p>
        }
        confirmLabel={t('admin.codeConfirm')}
        keepLabel={t('admin.codeKeep')}
        submitting={code.submitting}
        error={code.error}
        onConfirm={issueCode}
      />
      {account.status === 'active' ? (
        !isMe && (
          <ConfirmButton
            label={t('admin.suspend')}
            question={t('admin.suspendQuestion', { name: account.firstName })}
            details={
              <p>
                {t('admin.suspendDetails', { name: account.firstName })}
                {account.role === 'driver' && t('admin.suspendDriver')}
                {account.role === 'rider' && t('admin.suspendRider')}
                {t('admin.suspendReactivate')}
              </p>
            }
            confirmLabel={t('admin.suspendConfirm')}
            keepLabel={t('admin.suspendKeep')}
            submitting={status.submitting}
            error={status.error}
            onConfirm={() => setStatus('suspended')}
          />
        )
      ) : (
        <>
          {status.error && (
            <p role="alert" className="alert alert-error">
              {status.error}
            </p>
          )}
          <button
            type="button"
            className="button button-block button-secondary"
            onClick={() => setStatus('active')}
            disabled={status.submitting}
          >
            {status.submitting ? t('common.sending') : t('admin.reactivate')}
          </button>
        </>
      )}
    </>
  );
}
