import { useState } from 'react';
import { Link } from 'react-router-dom';

import { CheckboxField } from '../components/form/CheckboxField';
import { Form } from '../components/form/Form';
import { PasswordField } from '../components/form/PasswordField';
import { TextField } from '../components/form/TextField';
import { useRegister } from '../hooks/useAuthForms';

/** Rider registration. Drivers and staff are created by an administrator. */
export function RegisterPage() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [needsAccessibleVehicle, setNeedsAccessibleVehicle] = useState(false);
  const { submit, submitting, error, errors } = useRegister();

  function send() {
    submit({ firstName, lastName, phone, password, email: email.trim() || null, needsAccessibleVehicle });
  }

  return (
    <section>
      <h1>Créer un compte</h1>
      <Form onSubmit={send} submitLabel="Créer mon compte" submitting={submitting} error={error}>
        <TextField label="Prénom" value={firstName} onChange={setFirstName} autoComplete="given-name" required error={errors.firstName} />
        <TextField label="Nom" value={lastName} onChange={setLastName} autoComplete="family-name" required error={errors.lastName} />
        <TextField
          label="Numéro de téléphone"
          hint="Il servira à vous connecter."
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
    </section>
  );
}
