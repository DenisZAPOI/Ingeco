import { Link, useSearchParams } from 'react-router-dom';

import { PageHero, PageSheet } from '../components/layout/PageHero';
import { RideList } from '../components/rides/RideCard';
import { ErrorAlert } from '../components/ui/ErrorAlert';
import { RequestState } from '../components/ui/RequestState';
import { usePastRides, useUpcomingRides } from '../hooks/useRides';
import { t } from '../i18n';
import { BOOKING_PATHS } from '../lib/paths';

// In the address: the Back button returns to the tab the user was on.
const TAB_PARAM = 'onglet';
const PAST_TAB = 'passes';

/** The rider's trips in two tabs. Both lists load at once: switching costs no wait. */
export function RidesPage() {
  const [params, setParams] = useSearchParams();
  const showPast = params.get(TAB_PARAM) === PAST_TAB;
  const upcoming = useUpcomingRides();
  const past = usePastRides();

  function show(pastTab: boolean) {
    setParams(pastTab ? { [TAB_PARAM]: PAST_TAB } : {}, { replace: true });
  }

  return (
    <section>
      <PageHero title={t('rides.title')} />
      <PageSheet>
        <div className="tabs" role="tablist" aria-label={t('rides.title')}>
          <Tab label={t('rides.upcoming')} selected={!showPast} onSelect={() => show(false)} />
          <Tab label={t('rides.past')} selected={showPast} onSelect={() => show(true)} />
        </div>
        <div role="tabpanel">
          {showPast ? (
            <RequestState loading={past.loading} error={past.error} onRetry={past.retry}>
              {past.rides.length === 0 ? <p>{t('rides.noPast')}</p> : <RideList rides={past.rides} />}
              {past.moreError && <ErrorAlert message={past.moreError} onRetry={past.loadMore} />}
              {past.hasMore && !past.moreError && (
                <button
                  type="button"
                  className="button button-block button-secondary"
                  onClick={past.loadMore}
                  disabled={past.loadingMore}
                >
                  {past.loadingMore ? t('common.loading') : t('rides.more')}
                </button>
              )}
            </RequestState>
          ) : (
            <RequestState loading={upcoming.loading} error={upcoming.error} onRetry={upcoming.retry}>
              {upcoming.data?.items.length ? (
                <RideList rides={upcoming.data.items} />
              ) : (
                <>
                  <p>{t('rides.noUpcoming')}</p>
                  <Link to={BOOKING_PATHS.pickup} className="button button-block">
                    {t('rides.book')}
                  </Link>
                </>
              )}
            </RequestState>
          )}
        </div>
      </PageSheet>
    </section>
  );
}

function Tab({ label, selected, onSelect }: { label: string; selected: boolean; onSelect: () => void }) {
  return (
    <button type="button" role="tab" className="tab" aria-selected={selected} onClick={onSelect}>
      {label}
    </button>
  );
}
