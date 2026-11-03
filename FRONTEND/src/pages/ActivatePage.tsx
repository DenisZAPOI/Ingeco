import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

import { PageHero, PageSheet } from '../components/layout/PageHero';
import { Form } from '../components/form/Form';
import { PasswordField } from '../components/form/PasswordField';
import { TextField } from '../components/form/TextField';
import { useActivate } from '../hooks/useAuthForms';
import { PASSWORD_RESET_PATH, sentPhoneFromState } from '../lib/paths';

/** First access of an account created by the team, or new password after a
 *  forgotten one (code received by SMS, or handed over by the call centre). */
export function ActivatePage() {
  const location = useLocation();
  const sentTo = sentPhoneFromState(location.state);
  const [phone, setPhone] = useState(sentTo ?? '');
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const { submit, submitting, error, errors } = useActivate();

  return (
    <section>
      <PageHero title="J'ai reçu un code" />
      <PageSheet>
        {sentTo ? (
          // Same words whether the number has an account or not: the API does not say.
          <p>
            Si le <strong>{sentTo}</strong> a un compte, un code à 8 chiffres vient de lui être envoyé par SMS. Il est
            valable 15 minutes. Choisissez ici votre nouveau mot de passe.
          </p>
        ) : (
          <p>
            Vous avez reçu un code à 8 chiffres, par SMS ou par le centre d'appel. Choisissez ici votre mot de passe.
          </p>
        )}
        <Form
          onSubmit={() => submit({ phone, code, password })}
          submitLabel="Valider"
          submitting={submitting}
          error={error}
        >
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
          <TextField
            label="Code reçu"
            value={code}
            onChange={setCode}
            inputMode="numeric"
            autoComplete="one-time-code"
            placeholder="1234 5678"
            required
            error={errors.code}
          />
          <PasswordField
            label="Nouveau mot de passe"
            value={password}
            onChange={setPassword}
            autoComplete="new-password"
            error={errors.password}
          />
        </Form>
        <p className="note">
          Pas de code, ou code expiré ? <Link to={PASSWORD_RESET_PATH}>Recevoir un nouveau code par SMS</Link>
        </p>
      </PageSheet>
    </section>
  );
}
