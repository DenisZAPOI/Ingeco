import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { Form } from '../components/form/Form';
import { TextField } from '../components/form/TextField';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { useAskPasswordResetCode } from '../hooks/useAuthForms';
import { t } from '../i18n';
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
      <PageHero title={t('auth.resetTitle')} />
      <PageSheet>
        <p>{t('auth.resetIntro')}</p>
        <Form onSubmit={send} submitLabel={t('auth.sendCodeBySms')} submitting={submitting} error={error}>
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
        </Form>
        <p className="note">
          {t('auth.resetNoSms')}
        </p>
        <p className="note">
          <Link to={LOGIN_PATH}>{t('auth.backToLogin')}</Link>
        </p>
      </PageSheet>
    </section>
  );
}
