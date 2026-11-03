import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

import { PageHero, PageSheet } from '../components/layout/PageHero';
import { Form } from '../components/form/Form';
import { PasswordField } from '../components/form/PasswordField';
import { TextField } from '../components/form/TextField';
import { useActivate } from '../hooks/useAuthForms';
import { t } from '../i18n';
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
      <PageHero title={t('auth.activateTitle')} />
      <PageSheet>
        {sentTo ? (
          // Same words whether the number has an account or not: the API does not say.
          <p>
            {t('auth.activateSentBefore')} <strong>{sentTo}</strong> {t('auth.activateSentAfter')}
          </p>
        ) : (
          <p>
            {t('auth.activateIntro')}
          </p>
        )}
        <Form
          onSubmit={() => submit({ phone, code, password })}
          submitLabel={t('auth.activateSubmit')}
          submitting={submitting}
          error={error}
        >
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
          <TextField
            label={t('fields.code')}
            value={code}
            onChange={setCode}
            inputMode="numeric"
            autoComplete="one-time-code"
            placeholder="1234 5678"
            required
            error={errors.code}
          />
          <PasswordField
            label={t('fields.newPassword')}
            value={password}
            onChange={setPassword}
            autoComplete="new-password"
            error={errors.password}
          />
        </Form>
        <p className="note">
          {t('auth.noCode')} <Link to={PASSWORD_RESET_PATH}>{t('auth.newCodeBySms')}</Link>
        </p>
      </PageSheet>
    </section>
  );
}
