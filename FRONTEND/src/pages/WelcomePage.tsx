import { Link } from 'react-router-dom';

import { HomeIllustration } from '../components/home/HomeIllustration';
import { NeedCards } from '../components/home/NeedCards';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { CarIcon, TicketIcon, WheelchairIcon } from '../components/ui/icons';
import { t } from '../i18n';

const BENEFITS = [
  { Icon: CarIcon, key: 'welcome.benefitDriver' },
  { Icon: TicketIcon, key: 'welcome.benefitFunding' },
  { Icon: WheelchairIcon, key: 'welcome.benefitAccessible' },
] as const;

/** First screen of a visitor: the three needs, then the account access, then
 *  what the trips offer. Copied in index.html, shown before the app has
 *  loaded: change both together. */
export function WelcomePage() {
  return (
    <section>
      <PageHero title={t('welcome.title')} art={<HomeIllustration />}>
        <p className="hero-lead">{t('welcome.lead')}</p>
      </PageHero>
      <PageSheet>
        {/* Jobs and help are public: someone can look before creating an account. */}
        <NeedCards />

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

        <h2 className="benefits-title">{t('welcome.benefitsTitle')}</h2>
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
      </PageSheet>
    </section>
  );
}
