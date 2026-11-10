import { Link } from 'react-router-dom';

import { PageHero, PageSheet } from '../components/layout/PageHero';
import { t } from '../i18n';
import { JOBS_PATH } from '../lib/paths';
import { TRAINING_CATALOGUES } from '../lib/trainings';

/** Training (module M3): the catalogues that already exist, one link each.
 *  Same tab: the phone's Back button returns to the app, which people not at
 *  ease with a phone find more easily than another tab. */
export function TrainingsPage() {
  return (
    <section>
      <PageHero title={t('trainings.title')}>
        <p className="hero-lead">{t('trainings.lead')}</p>
      </PageHero>
      <PageSheet>
        {TRAINING_CATALOGUES.map(({ id, url }) => (
          <div key={id} className="panel">
            <h2 className="panel-title">{t(`trainings.catalogues.${id}.name`)}</h2>
            <p>{t(`trainings.catalogues.${id}.description`)}</p>
            {/* The text names the site: the user knows they leave the app. */}
            <a href={url} className="button button-block button-secondary" rel="noopener noreferrer">
              {t(`trainings.catalogues.${id}.open`)}
            </a>
          </div>
        ))}
        <p className="note">{t('trainings.outside')}</p>
        <Link to={JOBS_PATH} className="link-action">
          {t('trainings.backToJobs')}
        </Link>
      </PageSheet>
    </section>
  );
}
