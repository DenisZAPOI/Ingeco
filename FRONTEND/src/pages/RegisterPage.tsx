import { useState } from 'react';
import { Link } from 'react-router-dom';

import type { RegisterData } from '../api/auth';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { CheckboxField } from '../components/form/CheckboxField';
import { Form } from '../components/form/Form';
import { PasswordField } from '../components/form/PasswordField';
import { TextField } from '../components/form/TextField';
import { useAskRegistrationCode, useConfirmRegistration } from '../hooks/useAuthForms';

/** Rider registration, in two steps: the details, then the code received by
 *  SMS, which proves the phone. Drivers and staff are created by an administrator. */
export function RegisterPage() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [needsAccessibleVehicle, setNeedsAccessibleVehicle] = useState(false);
  // The details as sent, once the code is on its way: "Renvoyer" sends them again.
  const [sent, setSent] = useState<RegisterData | null>(null);
  const { submit, submitting, error, errors } = useAskRegistrationCode();

  async function send() {
    const data = { firstName, lastName, phone, password, email: email.trim() || null, needsAccessibleVehicle };
    if (await submit(data)) {
      setSent(data);
    }
  }

  if (sent) {
    return <CodeStep details={sent} onChangeDetails={() => setSent(null)} />;
  }

  return (
    <section>
      <PageHero title="Créer un compte" />
      <PageSheet>
        <Form onSubmit={send} submitLabel="Recevoir mon code par SMS" submitting={submitting} error={error}>
          <TextField label="Prénom" value={firstName} onChange={setFirstName} autoComplete="given-name" required error={errors.firstName} />
          <TextField label="Nom" value={lastName} onChange={setLastName} autoComplete="family-name" required error={errors.lastName} />
          <TextField
            label="Numéro de téléphone"
            hint="Il servira à vous connecter. Vous allez recevoir un code par SMS."
            value={phone}
            onChange={setPhone}
            type="tel"
            inputMode="tel"
            autoComplete="tel"
            placeholder="0694 12 34 56"
            required
            error={errors.phone}
          />
          <PasswordField
            label="Mot de passe"
            value={password}
            onChange={setPassword}
            autoComplete="new-password"
            error={errors.password}
          />
          <TextField
            label="Adresse e-mail (facultatif)"
            value={email}
            onChange={setEmail}
            type="email"
            inputMode="email"
            autoComplete="email"
            error={errors.email}
          />
          <CheckboxField
            label="J'ai besoin d'un véhicule adapté (fauteuil roulant)"
            checked={needsAccessibleVehicle}
            onChange={setNeedsAccessibleVehicle}
            error={errors.needsAccessibleVehicle}
          />
        </Form>
        <p className="note">
          Déjà un compte ? <Link to="/connexion">Se connecter</Link>
        </p>
      </PageSheet>
    </section>
  );
}

/** Second step: the code received by SMS creates the account and logs in. */
function CodeStep({ details, onChangeDetails }: { details: RegisterData; onChangeDetails: () => void }) {
  const [code, setCode] = useState('');
  const confirm = useConfirmRegistration();
  const resend = useAskRegistrationCode();
  const [resent, setResent] = useState(false);

  async function sendAgain() {
    setResent(false);
    if (await resend.submit(details)) {
      setResent(true);
    }
  }

  return (
    <section>
      <PageHero title="Code reçu par SMS" />
      <PageSheet>
        <p>
          Nous avons envoyé un code à 6 chiffres au <strong>{details.phone}</strong>. Il est valable 10 minutes.
        </p>
        <Form
          onSubmit={() => confirm.submit({ phone: details.phone, code })}
          submitLabel="Créer mon compte"
          submitting={confirm.submitting}
          error={confirm.error ?? resend.error}
          success={resent ? 'Un nouveau code vous a été envoyé.' : null}
        >
          <TextField
            label="Code reçu"
            value={code}
            onChange={setCode}
            inputMode="numeric"
            autoComplete="one-time-code"
            placeholder="123456"
            required
            error={confirm.errors.code}
          />
        </Form>
        <div className="stack">
          <button type="button" className="button button-block button-secondary" onClick={sendAgain} disabled={resend.submitting}>
            {resend.submitting ? 'Envoi…' : 'Renvoyer le code'}
          </button>
          <button type="button" className="button button-block button-secondary" onClick={onChangeDetails}>
            Changer de numéro
          </button>
        </div>
        <p className="note">
          Ce numéro a déjà un compte ? Le SMS vous le dit : <Link to="/connexion">connectez-vous</Link>.
        </p>
      </PageSheet>
    </section>
  );
}
