import { Link } from 'react-router-dom';

import { PageHero, PageSheet } from '../components/layout/PageHero';
import { t } from '../i18n';
import { LOGIN_PATH, ORIENTATION_PLAN_PATH, REGISTER_PATH } from '../lib/paths';

/** « Garder mon plan »: a plan is kept only with an account (minimisation, §2).
 *  After login or registration, the plan page keeps the answers still on the phone. */
export function OrientationKeepPage() {
  const back = { returnTo: ORIENTATION_PLAN_PATH };
  return (
    <section>
      <PageHero title={t('orientation.keepTitle')}>
        <p className="hero-lead">{t('orientation.keepLead')}</p>
      </PageHero>
      <PageSheet>
        <p>{t('orientation.keepWithout')}</p>
        <p>{t('orientation.keepWith')}</p>
        <div className="stack">
          <Link to={REGISTER_PATH} state={back} className="button button-block">
            {t('orientation.createAccount')}
          </Link>
          <Link to={LOGIN_PATH} state={back} className="button button-block button-secondary">
            {t('orientation.haveAccount')}
          </Link>
          <Link to={ORIENTATION_PLAN_PATH} className="link-action">
            {t('orientation.backToPlan')}
          </Link>
        </div>
      </PageSheet>
    </section>
  );
}
