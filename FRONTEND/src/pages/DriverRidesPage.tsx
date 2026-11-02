import { useSearchParams } from 'react-router-dom';

import { AvailabilityToggle } from '../components/driver/AvailabilityToggle';
import { OfferList } from '../components/driver/OfferList';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { RideList } from '../components/rides/RideCard';
import { ErrorAlert } from '../components/ui/ErrorAlert';
import { RequestState } from '../components/ui/RequestState';
import { usePastRides, useUpcomingRides } from '../hooks/useRides';
import { useSession } from '../hooks/useSession';

// In the address: the Back button returns to the tab the driver was on.
const TAB_PARAM = 'onglet';
const TABS = [
  { key: 'maintenant', label: 'Maintenant' },
  { key: 'plus-tard', label: 'Plus tard' },
  { key: 'mes-courses', label: 'Mes courses' },
] as const;
type TabKey = (typeof TABS)[number]['key'];

/** Rides offered to the driver, and their own. */
export function DriverRidesPage() {
  const [params, setParams] = useSearchParams();
  const tab: TabKey = TABS.find((entry) => entry.key === params.get(TAB_PARAM))?.key ?? 'maintenant';

  return (
    <section>
      <PageHero title="Courses" />
      <PageSheet>
        <div className="tabs" role="tablist" aria-label="Courses">
          {TABS.map((entry) => (
            <button
              key={entry.key}
              type="button"
              role="tab"
              className="tab"
              aria-selected={tab === entry.key}
              onClick={() => setParams({ [TAB_PARAM]: entry.key }, { replace: true })}
            >
              {entry.label}
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
      <h2>À faire</h2>
      <RequestState loading={upcoming.loading} error={upcoming.error} onRetry={upcoming.retry}>
        {upcoming.data?.items.length ? (
          <RideList rides={upcoming.data.items} forDriver />
        ) : (
          <p>Aucune course acceptée.</p>
        )}
      </RequestState>
      <h2>Passées</h2>
      <RequestState loading={past.loading} error={past.error} onRetry={past.retry}>
        {past.rides.length ? <RideList rides={past.rides} forDriver /> : <p>Aucune course passée.</p>}
        {past.moreError && <ErrorAlert message={past.moreError} onRetry={past.loadMore} />}
        {past.hasMore && !past.moreError && (
          <button
            type="button"
            className="button button-block button-secondary"
            onClick={past.loadMore}
            disabled={past.loadingMore}
          >
            {past.loadingMore ? 'Chargement…' : 'Voir plus de courses'}
          </button>
        )}
      </RequestState>
    </>
  );
}
