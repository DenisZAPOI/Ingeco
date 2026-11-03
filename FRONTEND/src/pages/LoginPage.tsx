import { useState } from 'react';
import { Link } from 'react-router-dom';

import { PageHero, PageSheet } from '../components/layout/PageHero';
import { Form } from '../components/form/Form';
import { PasswordField } from '../components/form/PasswordField';
import { TextField } from '../components/form/TextField';
import { useLogin } from '../hooks/useAuthForms';
import { t } from '../i18n';
import { PASSWORD_RESET_PATH } from '../lib/paths';

export function LoginPage() {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const { submit, submitting, error, errors } = useLogin();

  // Once logged in, the session context switches the routes to the user's home.
  return (
    <section>
      <PageHero title={t('auth.loginTitle')} />
      <PageSheet>
        <Form onSubmit={() => submit({ phone, password })} submitLabel={t('auth.loginSubmit')} submitting={submitting} error={error}>
          <TextField
            label={t('fields.phone')}
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
            autoComplete="current-password"
            error={errors.password}
          />
        </Form>
        <p className="note">
          <Link to={PASSWORD_RESET_PATH}>{t('auth.forgotPassword')}</Link>
        </p>
        <p className="note">
          {t('auth.noAccount')} <Link to="/inscription">{t('auth.createAccount')}</Link>
        </p>
      </PageSheet>
    </section>
  );
}
