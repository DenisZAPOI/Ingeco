import { Link } from 'react-router-dom';

import { PageHero, PageSheet } from '../components/layout/PageHero';
import { ArrowRightIcon, BriefcaseIcon, CarIcon, PhoneIcon, TicketIcon, WheelchairIcon } from '../components/ui/icons';
import { t } from '../i18n';
import { JOBS_PATH } from '../lib/paths';
import { formatPhone } from '../lib/phone';

// Given by the client, in international format (+594…). Until then the help
// block stays hidden: a wrong number would be worse than none.
const CALL_CENTER_PHONE: string | null = import.meta.env.VITE_CALL_CENTER_PHONE || null;

const BENEFITS = [
  { Icon: CarIcon, key: 'welcome.benefitDriver' },
  { Icon: TicketIcon, key: 'welcome.benefitFunding' },
  { Icon: WheelchairIcon, key: 'welcome.benefitAccessible' },
] as const;

/** First screen of a visitor: what the service is, then one main choice.
 *  Copied in index.html, shown before the app has loaded: change both together. */
export function WelcomePage() {
  return (
    <section>
      <PageHero title={t('welcome.title')}>
        <p className="hero-lead">{t('welcome.lead')}</p>
      </PageHero>
      <PageSheet>
        <ul className="benefits">
          {BENEFITS.map(({ Icon, key }) => (
            <li key={key} className="benefit">
              <span className="icon-chip">
                <Icon />
              </span>
              {t(key)}
            </li>
          ))}
        </ul>

        {/* Offers are public: someone can look before creating an account. */}
        <Link to={JOBS_PATH} className="action-card">
          <span className="icon-chip">
            <BriefcaseIcon />
          </span>
          <span className="action-card-text">
            <span className="action-card-title">{t('home.jobs')}</span>
            <span className="action-card-hint">{t('home.jobsHint')}</span>
          </span>
          <ArrowRightIcon className="action-card-arrow" />
        </Link>

        <nav className="stack" aria-label={t('welcome.accountNav')}>
          <Link to="/inscription" className="button button-block">
            {t('welcome.register')}
          </Link>
          <Link to="/connexion" className="button button-block button-secondary">
            {t('welcome.login')}
          </Link>
        </nav>

        <p className="note">
          {t('welcome.codeQuestion')}{' '}
          <Link to="/activation" className="link-action">
            {t('welcome.codeLink')}
          </Link>
        </p>

        {CALL_CENTER_PHONE && (
          <div className="panel help">
            <h2>{t('welcome.helpTitle')}</h2>
            <p>{t('welcome.helpText')}</p>
            {/* In full, for someone who dials it from another phone. */}
            <p className="help-phone">{formatPhone(CALL_CENTER_PHONE)}</p>
            <a href={`tel:${CALL_CENTER_PHONE}`} className="button button-block button-secondary">
              <PhoneIcon className="button-icon" />
              {t('welcome.call')}
            </a>
          </div>
        )}
      </PageSheet>
    </section>
  );
}
