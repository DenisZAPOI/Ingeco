import { useUpcomingRides } from '../../hooks/useRides';
import { t } from '../../i18n';
import { RideCard } from './RideCard';

/** The rider's next trip, first on the home screen. Nothing while it loads:
 *  the home screen stays usable without it. */
export function NextRide() {
  const upcoming = useUpcomingRides();
  const next = upcoming.data?.items[0];

  if (upcoming.error) {
    return (
      <p className="note">
        {t('ride.nextFailed')}{' '}
        <button type="button" className="link-button" onClick={upcoming.retry}>
          {t('common.retry')}
        </button>
      </p>
    );
  }
  if (!next) return null;
  return (
    <>
      <h2>{t('ride.nextTitle')}</h2>
      <RideCard ride={next} />
    </>
  );
}
