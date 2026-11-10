import { useSearchParams } from 'react-router-dom';

import { JobFilters } from '../components/jobs/JobFilters';
import { JobList } from '../components/jobs/JobCard';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { RequestState } from '../components/ui/RequestState';
import { useJobOffers } from '../hooks/useJobOffers';
import { t, tn } from '../i18n';
import { NO_FILTER, filterJobOffers, filtersFromParams, filtersToParams, offerCommunes, type JobFilters as Filters } from '../lib/jobs';

/** The job offers (module M2), public. One call for the whole list, then the
 *  filters run on the phone: instant, even on a slow network. */
export function JobsPage() {
  const offers = useJobOffers();
  const [params, setParams] = useSearchParams();
  const filters = filtersFromParams(params);
  const all = offers.data ?? [];
  const shown = filterJobOffers(all, filters);

  function change(next: Filters) {
    // replace: the Back button leaves the list, it does not undo each filter.
    setParams(filtersToParams(next), { replace: true });
  }

  return (
    <section>
      <PageHero title={t('jobs.title')}>
        <p className="hero-lead">{t('jobs.lead')}</p>
      </PageHero>
      <PageSheet>
        <RequestState loading={offers.loading && !offers.data} error={offers.error} onRetry={offers.retry}>
          <JobFilters communes={offerCommunes(all)} value={filters} onChange={change} />
          <p aria-live="polite" className="note">
            {tn('jobs.count', shown.length)}
          </p>
          {shown.length > 0 ? (
            <JobList offers={shown} />
          ) : (
            <>
              <p>{t('jobs.noMatch')}</p>
              <button type="button" className="button button-block button-secondary" onClick={() => change(NO_FILTER)}>
                {t('jobs.clearFilters')}
              </button>
            </>
          )}
          <p className="note">{t('jobs.fictional')}</p>
        </RequestState>
      </PageSheet>
    </section>
  );
}
