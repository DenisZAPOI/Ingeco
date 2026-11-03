import { useState } from 'react';
import { Link } from 'react-router-dom';

import type { RegisterData } from '../api/auth';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { CheckboxField } from '../components/form/CheckboxField';
import { Form } from '../components/form/Form';
import { PasswordField } from '../components/form/PasswordField';
import { TextField } from '../components/form/TextField';
import { useAskRegistrationCode, useConfirmRegistration } from '../hooks/useAuthForms';
import { t } from '../i18n';

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
      <PageHero title={t('auth.registerTitle')} />
      <PageSheet>
        <Form onSubmit={send} submitLabel={t('auth.sendCodeBySms')} submitting={submitting} error={error}>
          <TextField label={t('fields.firstName')} value={firstName} onChange={setFirstName} autoComplete="given-name" required error={errors.firstName} />
          <TextField label={t('fields.lastName')} value={lastName} onChange={setLastName} autoComplete="family-name" required error={errors.lastName} />
          <TextField
            label={t('fields.phone')}
            hint={t('auth.phoneHint')}
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
            label={t('fields.password')}
            value={password}
            onChange={setPassword}
            autoComplete="new-password"
            error={errors.password}
          />
          <TextField
            label={t('fields.emailOptional')}
            value={email}
            onChange={setEmail}
            type="email"
            inputMode="email"
            autoComplete="email"
            error={errors.email}
          />
          <CheckboxField
            label={t('fields.accessibleVehicle')}
            checked={needsAccessibleVehicle}
            onChange={setNeedsAccessibleVehicle}
            error={errors.needsAccessibleVehicle}
          />
        </Form>
        <p className="note">
          {t('auth.hasAccount')} <Link to="/connexion">{t('auth.loginTitle')}</Link>
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
      <PageHero title={t('auth.codeTitle')} />
      <PageSheet>
        <p>
          {t('auth.codeSentBefore')} <strong>{details.phone}</strong>
          {t('auth.codeSentAfter')}
        </p>
        <Form
          onSubmit={() => confirm.submit({ phone: details.phone, code })}
          submitLabel={t('auth.confirmSubmit')}
          submitting={confirm.submitting}
          error={confirm.error ?? resend.error}
          success={resent ? t('auth.codeResent') : null}
        >
          <TextField
            label={t('fields.code')}
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
            {resend.submitting ? t('auth.resending') : t('auth.resend')}
          </button>
          <button type="button" className="button button-block button-secondary" onClick={onChangeDetails}>
            {t('auth.changeNumber')}
          </button>
        </div>
        <p className="note">
          {t('auth.numberTaken')} <Link to="/connexion">{t('auth.numberTakenLink')}</Link>.
        </p>
      </PageSheet>
    </section>
  );
}
