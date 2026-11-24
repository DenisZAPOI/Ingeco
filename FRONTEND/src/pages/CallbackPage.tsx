import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

import { requestCallback } from '../api/support';
import { Form } from '../components/form/Form';
import { TextField } from '../components/form/TextField';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { PrivacyNote } from '../components/ui/PrivacyNote';
import { useSession } from '../hooks/useSession';
import { useSubmit } from '../hooks/useSubmit';
import { t } from '../i18n';
import { formatPhone } from '../lib/phone';
import { HELP_PATH, ORIENTATION_PLAN_PATH } from '../lib/paths';

/** « Être rappelé » (cahier des charges §6 and §7.1): the human contact of the
 *  action plan. Open to visitors; the number of a logged-in user is filled in,
 *  and may be changed. */
export function CallbackPage() {
  const { user } = useSession();
  const location = useLocation();
  const fromPlan = typeof location.state === 'object' && location.state !== null && 'fromPlan' in location.state;
  // null until the person types: the account's number fills in as soon as the
  // session is read, even after the page appeared.
  const [typed, setTyped] = useState<string | null>(null);
  const phone = typed ?? (user ? formatPhone(user.phone) : '');
  const [sent, setSent] = useState(false);
  const send = useSubmit(requestCallback);

  async function submit() {
    // `undefined` on success (204): null means it failed.
    const result = await send.submit(phone);
    if (result !== null) setSent(true);
  }

  const back = (
    <Link to={fromPlan ? ORIENTATION_PLAN_PATH : HELP_PATH} className="link-action">
      {fromPlan ? t('orientation.backToPlan') : t('callback.back')}
    </Link>
  );

  return (
    <section>
      <PageHero title={t('callback.title')}>{!sent && <p className="hero-lead">{t('callback.lead')}</p>}</PageHero>
      <PageSheet>
        {sent ? (
          // Shown only once the API has recorded the request: never a false confirmation.
          <div role="status" className="alert alert-success">
            <p>
              <strong>{t('callback.sent')}</strong>
            </p>
            <p>{t('callback.sentText', { phone })}</p>
            <p>{t('callback.noRobot')}</p>
          </div>
        ) : (
          <Form onSubmit={submit} submitLabel={t('callback.submit')} submitting={send.submitting} error={send.error}>
            <TextField
              label={t('callback.phone')}
              hint={t('callback.phoneHint')}
              value={phone}
              onChange={setTyped}
              type="tel"
              autoComplete="tel"
              inputMode="tel"
              error={send.errors.phone}
            />
            <p className="note">{t('callback.notice')}</p>
          </Form>
        )}
        <PrivacyNote />
        <div className="stack">{back}</div>
      </PageSheet>
    </section>
  );
}
