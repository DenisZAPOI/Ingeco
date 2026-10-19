import { useState } from 'react';
import { Link } from 'react-router-dom';

import { Form } from '../components/form/Form';
import { PasswordField } from '../components/form/PasswordField';
import { TextField } from '../components/form/TextField';
import { useLogin } from '../hooks/useAuthForms';

export function LoginPage() {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const { submit, submitting, error, errors } = useLogin();

  // Once logged in, the session context switches the routes to the user's home.
  return (
    <section>
      <h1>Se connecter</h1>
      <Form onSubmit={() => submit({ phone, password })} submitLabel="Se connecter" submitting={submitting} error={error}>
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
        <PasswordField
          label="Mot de passe"
          value={password}
          onChange={setPassword}
          autoComplete="current-password"
          error={errors.password}
        />
      </Form>
      <p className="note">
        Mot de passe oublié ? Appelez le centre d'appel : on vous donnera un code, à saisir dans{' '}
        <Link to="/activation">« J'ai reçu un code »</Link>.
      </p>
      <p className="note">
        Pas encore de compte ? <Link to="/inscription">Créer un compte</Link>
      </p>
    </section>
  );
}
