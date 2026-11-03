import { useSession } from '../../hooks/useSession';
import { useSetAvailability } from '../../hooks/useDriver';
import { useDriverLocation } from '../../hooks/useDriverLocation';
import type { LocationStatus } from '../../context/driverLocationContext';
import { t } from '../../i18n';

function locationNote(status: LocationStatus): string | null {
  if (status === 'waiting') return t('driver.locationWaiting');
  if (status === 'denied') return t('driver.locationDenied');
  if (status === 'unavailable') return t('driver.locationUnavailable');
  return null;
}

/** The one large button of the driver: online or offline. */
export function AvailabilityToggle() {
  const { user, setUser } = useSession();
  const availability = useSetAvailability();
  const location = useDriverLocation();
  // Drawn from the hint until the API answers: the button waits for the real state.
  const online = user?.isAvailable === true;

  async function toggle() {
    if (!user) return;
    const answer = await availability.submit(!online);
    if (answer) setUser({ ...user, isAvailable: answer.isAvailable });
  }

  const label = online ? t('driver.goOffline') : t('driver.goOnline');
  const note = locationNote(location);
  return (
    <div className="availability">
      <p role="status" className="status">
        <span className={online ? 'availability-dot availability-dot-on' : 'availability-dot'} aria-hidden="true" />
        {online ? t('driver.online') : t('driver.offline')}
      </p>
      <p className="note">
        {online ? t('driver.onlineNote') : t('driver.offlineNote')}
      </p>
      {online && note && <p className="alert alert-info">{note}</p>}
      {availability.error && (
        <p role="alert" className="alert alert-error">
          {availability.error}
        </p>
      )}
      <button
        type="button"
        className={online ? 'button button-block button-secondary' : 'button button-block'}
        onClick={toggle}
        disabled={!user || availability.submitting}
      >
        {availability.submitting ? t('common.sending') : label}
      </button>
    </div>
  );
}
