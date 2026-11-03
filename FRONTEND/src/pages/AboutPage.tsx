import { PageHero, PageSheet } from '../components/layout/PageHero';
import { t } from '../i18n';
import { CLIENT_NAME, DATABASE_TEAM, DEVELOPERS, OSM_COPYRIGHT_URL } from '../lib/about';

/** What the app is (a student demonstrator, nothing real) and who made it.
 *  Public: linked from the footer of every screen. */
export function AboutPage() {
  return (
    <section>
      <PageHero title={t('about.title')} />
      <PageSheet>
        <h2>{t('about.demoTitle')}</h2>
        <p>{t('about.demoText')}</p>
        <ul>
          <li>{t('about.demoExamples')}</li>
          <li>{t('about.demoPayment')}</li>
          <li>{t('about.demoSms')}</li>
          <li>{t('about.demoDriver')}</li>
        </ul>

        <h2>{t('about.authorsTitle')}</h2>
        <p>{t('about.authorsText', { client: CLIENT_NAME ?? t('about.clientFallback') })}</p>
        <dl className="credits">
          <dt>{t('about.developers')}</dt>
          <dd>{DEVELOPERS.join(', ')}</dd>
          <dt>{t('about.databaseTeam')}</dt>
          <dd>{DATABASE_TEAM.join(', ')}</dd>
        </dl>

        <h2>{t('about.mapsTitle')}</h2>
        <p>
          {t('about.mapsText')} ©{' '}
          <a href={OSM_COPYRIGHT_URL} target="_blank" rel="noopener noreferrer">
            {t('about.osmContributors')}
          </a>
          .
        </p>
      </PageSheet>
    </section>
  );
}
