import { useState } from 'react';

import type { User } from '../api/auth';
import { CheckboxField } from '../components/form/CheckboxField';
import { Form } from '../components/form/Form';
import { PasswordField } from '../components/form/PasswordField';
import { TextField } from '../components/form/TextField';
import { useUpdateProfile } from '../hooks/useAuthForms';
import { useSession } from '../hooks/useSession';
import { formatPhone } from '../lib/phone';

export function ProfilePage() {
  const { user } = useSession();
  // The routes only show this page to a logged-in user.
  if (!user) return null;

  return (
    <section>
      <h1>Mon profil</h1>
      <p>
        Numéro de téléphone : <strong>{formatPhone(user.phone)}</strong>
        <br />
        <span className="note">Pour le changer, contactez le centre d'appel.</span>
      </p>
      <IdentityForm user={user} />
      <PasswordForm />
    </section>
  );
}

function IdentityForm({ user }: { user: User }) {
  const [firstName, setFirstName] = useState(user.firstName);
  const [lastName, setLastName] = useState(user.lastName);
  const [email, setEmail] = useState(user.email ?? '');
  const [needsAccessibleVehicle, setNeedsAccessibleVehicle] = useState(user.needsAccessibleVehicle ?? false);
  const [saved, setSaved] = useState(false);
  const { submit, submitting, error, errors } = useUpdateProfile();
  const isRider = user.role === 'rider';

  async function send() {
    setSaved(false);
    const result = await submit({
      firstName,
      lastName,
      email: email.trim() || null,
      ...(isRider && { needsAccessibleVehicle }),
    });
    setSaved(result !== null);
  }

  return (
    <>
      <h2>Mes informations</h2>
      <Form
        onSubmit={send}
        submitLabel="Enregistrer"
        submitting={submitting}
        error={error}
        success={saved ? 'Vos informations sont enregistrées.' : null}
      >
        <TextField label="Prénom" value={firstName} onChange={setFirstName} autoComplete="given-name" required error={errors.firstName} />
        <TextField label="Nom" value={lastName} onChange={setLastName} autoComplete="family-name" required error={errors.lastName} />
        <TextField
          label="Adresse e-mail (facultatif)"
          value={email}
          onChange={setEmail}
          type="email"
          inputMode="email"
          autoComplete="email"
          error={errors.email}
        />
        {isRider && (
          <CheckboxField
            label="J'ai besoin d'un véhicule adapté (fauteuil roulant)"
            checked={needsAccessibleVehicle}
            onChange={setNeedsAccessibleVehicle}
            error={errors.needsAccessibleVehicle}
          />
        )}
      </Form>
    </>
  );
}

function PasswordForm() {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [saved, setSaved] = useState(false);
  const { submit, submitting, error, errors } = useUpdateProfile();

  async function send() {
    setSaved(false);
    const result = await submit({ currentPassword, newPassword });
    if (result !== null) {
      setCurrentPassword('');
      setNewPassword('');
      setSaved(true);
    }
  }

  return (
    <>
      <h2>Changer de mot de passe</h2>
      <Form
        onSubmit={send}
        submitLabel="Changer le mot de passe"
        submitting={submitting}
        error={error}
        success={saved ? 'Votre mot de passe est changé.' : null}
      >
        <PasswordField
          label="Mot de passe actuel"
          value={currentPassword}
          onChange={setCurrentPassword}
          autoComplete="current-password"
          error={errors.currentPassword}
        />
        <PasswordField
          label="Nouveau mot de passe"
          value={newPassword}
          onChange={setNewPassword}
          autoComplete="new-password"
          error={errors.newPassword}
        />
      </Form>
    </>
  );
}
