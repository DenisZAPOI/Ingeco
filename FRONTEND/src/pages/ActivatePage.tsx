import { useState } from 'react';

import { Form } from '../components/form/Form';
import { PasswordField } from '../components/form/PasswordField';
import { TextField } from '../components/form/TextField';
import { useActivate } from '../hooks/useAuthForms';

/** First access of an account created by the team, or new password after a forgotten one. */
export function ActivatePage() {
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const { submit, submitting, error, errors } = useActivate();

  return (
    <section>
      <h1>J'ai reçu un code</h1>
      <p>Le centre d'appel ou l'équipe vous a donné un code à 8 chiffres. Choisissez ici votre mot de passe.</p>
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
    </section>
  );
}
