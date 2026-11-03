import type { Ride, RideAction } from '../../api/rides';
import { useDriveRide } from '../../hooks/useDriver';
import { useSession } from '../../hooks/useSession';
import { useSlowNetwork } from '../../hooks/useSlowNetwork';
import { t } from '../../i18n';
import { CallLink } from '../rides/DriverCard';
import { ConfirmButton } from '../ui/ConfirmButton';
import { DirectionsLink } from './DirectionsLink';

type DriverRideActionsProps = {
  ride: Ride;
  onChange: (ride: Ride) => void;
};

type MainLabel = 'driver.accept' | 'driver.start' | 'driver.complete';

const MAIN_ACTIONS: Partial<Record<Ride['status'], { action: RideAction; label: MainLabel }>> = {
  pending: { action: 'accept', label: 'driver.accept' },
  accepted: { action: 'start', label: 'driver.start' },
  in_progress: { action: 'complete', label: 'driver.complete' },
};

/** What the driver can do now with this ride, the main action first. */
export function DriverRideActions({ ride, onChange }: DriverRideActionsProps) {
  const { user } = useSession();
  const drive = useDriveRide(ride.id);
  // Its own state: an error of the release shows under its question, not under the main button.
  const release = useDriveRide(ride.id);
  const slow = useSlowNetwork(drive.submitting);
  const main = MAIN_ACTIONS[ride.status];

  async function run(action: RideAction) {
    const changed = await drive.submit(action);
    if (changed) onChange(changed);
  }

  async function giveUp() {
    const changed = await release.submit('release');
    if (changed) onChange(changed);
  }

  if (ride.status === 'pending' && user?.isAvailable === false) {
    return <p className="alert alert-info">{t('driver.beAvailable')}</p>;
  }

  return (
    <>
      {ride.rider && <CallLink name={ride.rider.firstName} phone={ride.rider.phone} />}
      {ride.status === 'accepted' && <DirectionsLink label={t('driver.directionsPickup')} to={ride.pickup} />}
      {ride.status === 'in_progress' && <DirectionsLink label={t('driver.directionsDropoff')} to={ride.dropoff} />}
      {main && (
        <div className="stack">
          {drive.error && (
            <p role="alert" className="alert alert-error">
              {drive.error}
            </p>
          )}
          {slow && (
            <p role="status" className="note">
              {t('common.sendingSlow')}
            </p>
          )}
          <button type="button" className="button button-block" onClick={() => run(main.action)} disabled={drive.submitting}>
            {drive.submitting ? t('common.sending') : t(main.label)}
          </button>
        </div>
      )}
      {ride.status === 'accepted' && (
        <ConfirmButton
          label={t('driver.release')}
          question={t('driver.releaseQuestion')}
          details={<p>{t('driver.releaseDetails')}</p>}
          confirmLabel={t('driver.releaseConfirm')}
          keepLabel={t('driver.releaseKeep')}
          submitting={release.submitting}
          error={release.error}
          onConfirm={giveUp}
        />
      )}
    </>
  );
}
