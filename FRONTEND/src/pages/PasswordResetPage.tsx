import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { Form } from '../components/form/Form';
import { TextField } from '../components/form/TextField';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { useAskPasswordResetCode } from '../hooks/useAuthForms';
import { ACTIVATION_PATH, LOGIN_PATH } from '../lib/paths';

/** Forgotten password: the number only. The code arrives by SMS and is typed
 *  on the activation page, which already sets a new password. */
export function PasswordResetPage() {
  const [phone, setPhone] = useState('');
  const { submit, submitting, error, errors } = useAskPasswordResetCode();
  const navigate = useNavigate();

  async function send() {
    if (await submit({ phone })) {
      navigate(ACTIVATION_PATH, { state: { sentTo: phone } });
    }
  }

  return (
    <section>
      <PageHero title="Mot de passe oublié" />
      <PageSheet>
        <p>Indiquez votre numéro. Vous allez recevoir un code par SMS pour choisir un nouveau mot de passe.</p>
        <Form onSubmit={send} submitLabel="Recevoir mon code par SMS" submitting={submitting} error={error}>
          <TextField
            label="Numéro de téléphone"
            value={phone}
            onChange={setPhone}
            type="tel"
            inputMode="tel"
            autoComplete="tel"
            placeholder="0694 12 34 56"
            required
            error={errors.phone}
          />
        </Form>
        <p className="note">
          Pas de SMS ? Le centre d'appel peut aussi vous donner un code.
        </p>
        <p className="note">
          <Link to={LOGIN_PATH}>Retour à la connexion</Link>
        </p>
      </PageSheet>
    </section>
  );
}
