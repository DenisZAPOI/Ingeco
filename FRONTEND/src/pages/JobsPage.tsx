import { useRef } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import { JobFilters } from '../components/jobs/JobFilters';
import { JobList } from '../components/jobs/JobCard';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { ArrowRightIcon, BookIcon, QuestionIcon } from '../components/ui/icons';
import { Pagination } from '../components/ui/Pagination';
import { RequestState } from '../components/ui/RequestState';
import { useJobOffers } from '../hooks/useJobOffers';
import { t, tn } from '../i18n';
import { ORIENTATION_PATH, TRAININGS_PATH } from '../lib/paths';
import { NO_FILTER, filterJobOffers, filtersFromParams, filtersToParams, offerCommunes, type JobFilters as Filters } from '../lib/jobs';
import { pageFromParams, pageToParams, paginate } from '../lib/pagination';

// Ten offers a page: about two screens of a phone.
const OFFERS_PER_PAGE = 10;

/** The job offers (module M2), public. One call for the whole list, then the
 *  filters and the pages run on the phone: instant, even on a slow network. */
export function JobsPage() {
  const offers = useJobOffers();
  const [params, setParams] = useSearchParams();
  const filters = filtersFromParams(params);
  const all = offers.data ?? [];
  const shown = filterJobOffers(all, filters);
  const current = paginate(shown, pageFromParams(params), OFFERS_PER_PAGE);
  const listStart = useRef<HTMLParagraphElement>(null);

  // A new filter starts again at the first page (no page in the address).
  function change(next: Filters) {
    // replace: the Back button leaves the list, it does not undo each filter.
    setParams(filtersToParams(next), { replace: true });
  }

  function changePage(page: number) {
    setParams({ ...filtersToParams(filters), ...pageToParams(page) }, { replace: true });
    // Back to the top of the list, where a screen reader also starts again.
    listStart.current?.focus({ preventScroll: true });
    listStart.current?.scrollIntoView({ block: 'start' });
  }

  return (
    <section>
      <PageHero title={t('jobs.title')} wide>
        <p className="hero-lead">{t('jobs.lead')}</p>
      </PageHero>
      <PageSheet wide>
        {/* The start of scenario A (§8): someone who does not know what to look for. */}
        <Link to={ORIENTATION_PATH} className="action-card action-card-primary">
          <span className="icon-chip icon-chip-sun">
            <QuestionIcon />
          </span>
          <span className="action-card-text">
            <span className="action-card-title">{t('orientation.entry')}</span>
            <span className="action-card-hint">{t('orientation.entryHint')}</span>
          </span>
          <ArrowRightIcon className="action-card-arrow" />
        </Link>
        <RequestState loading={offers.loading && !offers.data} error={offers.error} onRetry={offers.retry}>
          <JobFilters communes={offerCommunes(all)} value={filters} onChange={change} />
          <p aria-live="polite" className="note" ref={listStart} tabIndex={-1}>
            {tn('jobs.count', shown.length)}
          </p>
          {shown.length > 0 ? (
            <>
              <JobList offers={current.items} />
              <Pagination page={current.page} pageCount={current.pageCount} onChange={changePage} />
            </>
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
        {/* Outside the loading state: reachable even when the offers cannot load. */}
        <Link to={TRAININGS_PATH} className="action-card">
          <span className="icon-chip">
            <BookIcon />
          </span>
          <span className="action-card-text">
            <span className="action-card-title">{t('jobs.training')}</span>
            <span className="action-card-hint">{t('jobs.trainingHint')}</span>
          </span>
          <ArrowRightIcon className="action-card-arrow" />
        </Link>
      </PageSheet>
    </section>
  );
}
