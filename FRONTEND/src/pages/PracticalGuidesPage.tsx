import { Link } from 'react-router-dom';

import { GuideList } from '../components/help/GuideList';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { RequestState } from '../components/ui/RequestState';
import { usePracticalGuides } from '../hooks/usePracticalGuides';
import { t } from '../i18n';
import { HELP_PATH } from '../lib/paths';

/** Practical guides "Comment faire ?" (module M5), public: one per need. */
export function PracticalGuidesPage() {
  const guides = usePracticalGuides();

  return (
    <section>
      <PageHero title={t('guides.title')}>
        <p className="hero-lead">{t('guides.lead')}</p>
      </PageHero>
      <PageSheet>
        <RequestState loading={guides.loading && !guides.data} error={guides.error} onRetry={guides.retry}>
          <GuideList guides={guides.data ?? []} />
        </RequestState>
        <Link to={HELP_PATH} className="link-action">
          {t('helpServices.backToHelp')}
        </Link>
      </PageSheet>
    </section>
  );
}
