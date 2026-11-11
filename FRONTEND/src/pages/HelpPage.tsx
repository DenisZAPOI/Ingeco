import { Link } from 'react-router-dom';

import { CallCenterHelp } from '../components/help/CallCenterHelp';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { ArrowRightIcon, QuestionIcon } from '../components/ui/icons';
import { t } from '../i18n';
import { FAQ_PATH } from '../lib/paths';

/** "J'ai besoin d'aide" (third need of the home screen). Public, also linked
 *  from the footer. The directory of help services will be added here. */
export function HelpPage() {
  return (
    <section>
      <PageHero title={t('helpPage.title')}>
        <p className="hero-lead">{t('helpPage.lead')}</p>
      </PageHero>
      <PageSheet>
        <Link to={FAQ_PATH} className="action-card">
          <span className="icon-chip">
            <QuestionIcon />
          </span>
          <span className="action-card-text">
            <span className="action-card-title">{t('helpPage.faq')}</span>
            <span className="action-card-hint">{t('helpPage.faqHint')}</span>
          </span>
          <ArrowRightIcon className="action-card-arrow" />
        </Link>
        <CallCenterHelp />
      </PageSheet>
    </section>
  );
}
