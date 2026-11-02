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
import { ROLE_LABELS, accountFromState, activationFromState } from '../lib/accounts';
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
      <PageHero title={account.data ? `${account.data.firstName} ${account.data.lastName}` : 'Compte'} />
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
          Voir tous les comptes
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
          <h2>Photo</h2>
          <p className="note">Le passager la verra pour reconnaître son chauffeur.</p>
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
      <dt>Rôle</dt>
      <dd>{ROLE_LABELS[account.role]}</dd>
      <dt>Téléphone</dt>
      <dd>{formatPhone(account.phone)}</dd>
      {account.email && (
        <>
          <dt>E-mail</dt>
          <dd>{account.email}</dd>
        </>
      )}
      <dt>Statut</dt>
      <dd>
        {account.status === 'suspended' ? 'Suspendu' : 'Actif'}
        {!account.isActivated && ' · pas encore activé'}
      </dd>
      {account.role === 'rider' && account.needsAccessibleVehicle && (
        <>
          <dt>Besoin</dt>
          <dd>Véhicule adapté (fauteuil roulant)</dd>
        </>
      )}
      <dt>Créé le</dt>
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
      <h2>Usager prioritaire</h2>
      <p>
        {account.isPriority ? 'Cet usager est prioritaire.' : "Cet usager n'est pas prioritaire."}{' '}
        <span className="note">Sert au centre d'appel et aux statistiques.</span>
      </p>
      {error && (
        <p role="alert" className="alert alert-error">
          {error}
        </p>
      )}
      <button type="button" className="button button-block button-secondary" onClick={toggle} disabled={submitting}>
        {submitting ? 'Envoi en cours…' : account.isPriority ? 'Retirer la priorité' : 'Marquer comme prioritaire'}
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
      <h2>Véhicule</h2>
      <Form
        onSubmit={send}
        submitLabel="Enregistrer le véhicule"
        submitting={submitting}
        error={error}
        success={saved ? 'Le véhicule est enregistré.' : null}
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
      <h2>Accès</h2>
      <ConfirmButton
        key={codesIssued}
        label={account.isActivated ? 'Mot de passe oublié : nouveau code' : "Générer un code d'activation"}
        question={`Générer un nouveau code pour ${account.firstName} ?`}
        details={
          <p>
            L'ancien code, s'il y en avait un, ne marchera plus. Le mot de passe actuel reste valable.
            {account.isActivated && ' Un SMS prévient la personne.'}
          </p>
        }
        confirmLabel="Générer le code"
        keepLabel="Ne rien changer"
        submitting={code.submitting}
        error={code.error}
        onConfirm={issueCode}
      />
      {account.status === 'active' ? (
        !isMe && (
          <ConfirmButton
            label="Suspendre le compte"
            question={`Suspendre le compte de ${account.firstName} ?`}
            details={
              <p>
                {account.firstName} ne pourra plus se connecter, et ses sessions ouvertes prennent fin tout de suite.
                {account.role === 'driver' && ' Le chauffeur passe hors ligne et ne reçoit plus de course.'}
                {account.role === 'rider' && ' Ses trajets pas encore pris par un chauffeur sont annulés et remboursés.'} Vous pourrez réactiver
                le compte.
              </p>
            }
            confirmLabel="Suspendre"
            keepLabel="Ne pas suspendre"
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
            {status.submitting ? 'Envoi en cours…' : 'Réactiver le compte'}
          </button>
        </>
      )}
    </>
  );
}
