import { useSearchParams } from 'react-router-dom';

import { AvailabilityToggle } from '../components/driver/AvailabilityToggle';
import { OfferList } from '../components/driver/OfferList';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { RideList } from '../components/rides/RideCard';
import { ErrorAlert } from '../components/ui/ErrorAlert';
import { RequestState } from '../components/ui/RequestState';
import { usePastRides, useUpcomingRides } from '../hooks/useRides';
import { useSession } from '../hooks/useSession';
import { t } from '../i18n';

// In the address: the Back button returns to the tab the driver was on.
const TAB_PARAM = 'onglet';
const TABS = [
  { key: 'maintenant', label: 'driver.tabNow' },
  { key: 'plus-tard', label: 'driver.tabLater' },
  { key: 'mes-courses', label: 'driver.tabMine' },
] as const;
type TabKey = (typeof TABS)[number]['key'];

/** Rides offered to the driver, and their own. */
export function DriverRidesPage() {
  const [params, setParams] = useSearchParams();
  const tab: TabKey = TABS.find((entry) => entry.key === params.get(TAB_PARAM))?.key ?? 'maintenant';

  return (
    <section>
      <PageHero title={t('driver.rides')} />
      <PageSheet>
        <div className="tabs" role="tablist" aria-label={t('driver.rides')}>
          {TABS.map((entry) => (
            <button
              key={entry.key}
              type="button"
              role="tab"
              className="tab"
              aria-selected={tab === entry.key}
              onClick={() => setParams({ [TAB_PARAM]: entry.key }, { replace: true })}
            >
              {t(entry.label)}
            </button>
          ))}
        </div>
        <div role="tabpanel">
          {tab === 'mes-courses' ? <MyRides /> : <Offers type={tab === 'maintenant' ? 'immediate' : 'scheduled'} />}
        </div>
      </PageSheet>
    </section>
  );
}

/** Offers only while online: offline, the button to go online instead. */
function Offers({ type }: { type: 'immediate' | 'scheduled' }) {
  const { user } = useSession();
  if (user?.isAvailable !== true) {
    return <AvailabilityToggle />;
  }
  // key: each tab loads its own list.
  return <OfferList key={type} type={type} />;
}

function MyRides() {
  const upcoming = useUpcomingRides();
  const past = usePastRides();

  return (
    <>
      <h2>{t('driver.toDo')}</h2>
      <RequestState loading={upcoming.loading} error={upcoming.error} onRetry={upcoming.retry}>
        {upcoming.data?.items.length ? (
          <RideList rides={upcoming.data.items} forDriver />
        ) : (
          <p>{t('driver.noneAccepted')}</p>
        )}
      </RequestState>
      <h2>{t('driver.past')}</h2>
      <RequestState loading={past.loading} error={past.error} onRetry={past.retry}>
        {past.rides.length ? <RideList rides={past.rides} forDriver /> : <p>{t('driver.nonePast')}</p>}
        {past.moreError && <ErrorAlert message={past.moreError} onRetry={past.loadMore} />}
        {past.hasMore && !past.moreError && (
          <button
            type="button"
            className="button button-block button-secondary"
            onClick={past.loadMore}
            disabled={past.loadingMore}
          >
            {past.loadingMore ? t('common.loading') : t('driver.more')}
          </button>
        )}
      </RequestState>
    </>
  );
}
