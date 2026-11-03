import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import type { StaffRole } from '../api/admin';
import { VehicleFields } from '../components/admin/VehicleFields';
import { ChoiceGroup, type Choice } from '../components/form/ChoiceGroup';
import { Form } from '../components/form/Form';
import { TextField } from '../components/form/TextField';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { useCreateAccount } from '../hooks/useAdmin';
import { t } from '../i18n';
import { accountPath } from '../lib/accounts';
import { vehicleData, vehicleDraft } from '../lib/vehicle';

// Partner referents come with the vouchers (step 5); riders register themselves.
function roleChoices(): Choice<StaffRole>[] {
  return [
    { value: 'driver', label: t('admin.roles.driver') },
    { value: 'operator', label: t('admin.operatorChoice') },
    { value: 'admin', label: t('admin.roles.admin') },
  ];
}

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
      <PageHero title={t('admin.newTitle')} />
      <PageSheet>
        <Form onSubmit={send} submitLabel={t('admin.newSubmit')} submitting={submitting} error={error}>
          <ChoiceGroup
            legend={t('admin.role')}
            choices={roleChoices()}
            value={role}
            onChange={(chosen) => {
              setRole(chosen);
              setRoleMissing(false);
            }}
            error={roleMissing ? t('admin.roleMissing') : errors.role}
          />
          <TextField label={t('fields.firstName')} value={firstName} onChange={setFirstName} required error={errors.firstName} />
          <TextField label={t('fields.lastName')} value={lastName} onChange={setLastName} required error={errors.lastName} />
          <TextField
            label={t('fields.phone')}
            value={phone}
            onChange={setPhone}
            type="tel"
            inputMode="tel"
            hint={t('admin.phoneHint')}
            required
            error={errors.phone}
          />
          <TextField
            label={t('fields.emailOptional')}
            value={email}
            onChange={setEmail}
            type="email"
            inputMode="email"
            error={errors.email}
          />
          {role === 'driver' && (
            <fieldset className="field">
              <legend className="field-label">{t('admin.vehicle')}</legend>
              <p className="note">{t('admin.vehicleChecked')}</p>
              <VehicleFields draft={vehicle} onChange={setVehicle} errors={errors} prefix="vehicle" />
            </fieldset>
          )}
        </Form>
      </PageSheet>
    </section>
  );
}
