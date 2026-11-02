import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import type { StaffRole } from '../api/admin';
import { VehicleFields } from '../components/admin/VehicleFields';
import { ChoiceGroup, type Choice } from '../components/form/ChoiceGroup';
import { Form } from '../components/form/Form';
import { TextField } from '../components/form/TextField';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { useCreateAccount } from '../hooks/useAdmin';
import { accountPath } from '../lib/accounts';
import { vehicleData, vehicleDraft } from '../lib/vehicle';

// Partner referents come with the vouchers (step 5); riders register themselves.
const ROLE_CHOICES: Choice<StaffRole>[] = [
  { value: 'driver', label: 'Chauffeur' },
  { value: 'operator', label: "Opérateur (centre d'appel)" },
  { value: 'admin', label: 'Administrateur' },
];

/** UC52: an account without password. The next screen shows its activation code, once. */
export function AdminNewAccountPage() {
  const navigate = useNavigate();
  const [role, setRole] = useState<StaffRole | null>(null);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [vehicle, setVehicle] = useState(vehicleDraft(null));
  const { submit, submitting, error, errors } = useCreateAccount();
  const [roleMissing, setRoleMissing] = useState(false);

  async function send() {
    if (!role) {
      setRoleMissing(true);
      return;
    }
    const created = await submit({
      role,
      firstName,
      lastName,
      phone,
      email: email.trim() || null,
      vehicle: role === 'driver' ? vehicleData(vehicle) : null,
    });
    if (created) {
      // The code travels in the navigation state only: a reload does not show it again.
      navigate(accountPath(created.account.id), {
        replace: true,
        state: { account: created.account, activation: created.activation },
      });
    }
  }

  return (
    <section>
      <PageHero title="Créer un compte" />
      <PageSheet>
        <Form onSubmit={send} submitLabel="Créer le compte" submitting={submitting} error={error}>
          <ChoiceGroup
            legend="Rôle"
            choices={ROLE_CHOICES}
            value={role}
            onChange={(chosen) => {
              setRole(chosen);
              setRoleMissing(false);
            }}
            error={roleMissing ? 'Choisissez un rôle.' : errors.role}
          />
          <TextField label="Prénom" value={firstName} onChange={setFirstName} required error={errors.firstName} />
          <TextField label="Nom" value={lastName} onChange={setLastName} required error={errors.lastName} />
          <TextField
            label="Numéro de téléphone"
            value={phone}
            onChange={setPhone}
            type="tel"
            inputMode="tel"
            hint="Il servira à se connecter. Exemple : 0694 12 34 56"
            required
            error={errors.phone}
          />
          <TextField
            label="Adresse e-mail (facultatif)"
            value={email}
            onChange={setEmail}
            type="email"
            inputMode="email"
            error={errors.email}
          />
          {role === 'driver' && (
            <fieldset className="field">
              <legend className="field-label">Véhicule</legend>
              <p className="note">Après vérification en personne du permis, de l'assurance et de la carte VTC.</p>
              <VehicleFields draft={vehicle} onChange={setVehicle} errors={errors} prefix="vehicle" />
            </fieldset>
          )}
        </Form>
      </PageSheet>
    </section>
  );
}
