import { Link } from 'react-router-dom';

import { CallCenterHelp } from '../components/help/CallCenterHelp';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { ArrowRightIcon, FormIcon, LifebuoyIcon, QuestionIcon } from '../components/ui/icons';
import { t } from '../i18n';
import { FAQ_PATH, GUIDES_PATH, HELP_SERVICES_PATH } from '../lib/paths';

/** "J'ai besoin d'aide" (third need of the home screen). Public, also linked
 *  from the footer: the directory of help services first, then the practical
 *  guides and the questions. */
export function HelpPage() {
  return (
    <section>
      <PageHero title={t('helpPage.title')}>
        <p className="hero-lead">{t('helpPage.lead')}</p>
      </PageHero>
      <PageSheet>
        <div className="stack">
          <Link to={HELP_SERVICES_PATH} className="action-card action-card-primary">
            <span className="icon-chip icon-chip-sun">
              <LifebuoyIcon />
            </span>
            <span className="action-card-text">
              <span className="action-card-title">{t('helpPage.services')}</span>
              <span className="action-card-hint">{t('helpPage.servicesHint')}</span>
            </span>
            <ArrowRightIcon className="action-card-arrow" />
          </Link>
          <Link to={GUIDES_PATH} className="action-card">
            <span className="icon-chip">
              <FormIcon />
            </span>
            <span className="action-card-text">
              <span className="action-card-title">{t('helpPage.guides')}</span>
              <span className="action-card-hint">{t('helpPage.guidesHint')}</span>
            </span>
            <ArrowRightIcon className="action-card-arrow" />
          </Link>
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
        </div>
        <CallCenterHelp />
      </PageSheet>
    </section>
  );
}
