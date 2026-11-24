import { Link } from 'react-router-dom';

import { GuideList } from '../components/help/GuideList';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { Pagination } from '../components/ui/Pagination';
import { RequestState } from '../components/ui/RequestState';
import { useAddressPage } from '../hooks/useListPage';
import { usePracticalGuides } from '../hooks/usePracticalGuides';
import { t, tn } from '../i18n';
import { HELP_PATH } from '../lib/paths';

/** Practical guides "Comment faire ?" (module M5), public: one per need. */
export function PracticalGuidesPage() {
  const guides = usePracticalGuides();
  const current = useAddressPage(guides.data ?? []);

  return (
    <section>
      <PageHero title={t('guides.title')} wide>
        <p className="hero-lead">{t('guides.lead')}</p>
      </PageHero>
      <PageSheet wide>
        <RequestState loading={guides.loading && !guides.data} error={guides.error} onRetry={guides.retry}>
          <p className="note" ref={current.listStart} tabIndex={-1}>
            {tn('guides.count', guides.data?.length ?? 0)}
          </p>
          <GuideList guides={current.items} />
          <Pagination page={current.page} pageCount={current.pageCount} onChange={current.goTo} />
        </RequestState>
        <Link to={HELP_PATH} className="link-action">
          {t('helpServices.backToHelp')}
        </Link>
      </PageSheet>
    </section>
  );
}
