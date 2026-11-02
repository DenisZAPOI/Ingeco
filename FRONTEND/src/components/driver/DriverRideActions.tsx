import type { Ride, RideAction } from '../../api/rides';
import { useDriveRide } from '../../hooks/useDriver';
import { useSession } from '../../hooks/useSession';
import { useSlowNetwork } from '../../hooks/useSlowNetwork';
import { CallLink } from '../rides/DriverCard';
import { ConfirmButton } from '../ui/ConfirmButton';
import { DirectionsLink } from './DirectionsLink';

type DriverRideActionsProps = {
  ride: Ride;
  onChange: (ride: Ride) => void;
};

const MAIN_ACTIONS: Partial<Record<Ride['status'], { action: RideAction; label: string }>> = {
  pending: { action: 'accept', label: 'Accepter la course' },
  accepted: { action: 'start', label: 'Le passager est à bord : démarrer' },
  in_progress: { action: 'complete', label: 'Arrivé : terminer la course' },
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
    return <p className="alert alert-info">Mettez-vous disponible depuis l'accueil pour accepter cette course.</p>;
  }

  return (
    <>
      {ride.rider && <CallLink name={ride.rider.firstName} phone={ride.rider.phone} />}
      {ride.status === 'accepted' && <DirectionsLink label="Itinéraire vers le départ" to={ride.pickup} />}
      {ride.status === 'in_progress' && <DirectionsLink label="Itinéraire vers l'arrivée" to={ride.dropoff} />}
      {main && (
        <div className="stack">
          {drive.error && (
            <p role="alert" className="alert alert-error">
              {drive.error}
            </p>
          )}
          {slow && (
            <p role="status" className="note">
              Le réseau est lent. Ne fermez pas l'application, l'envoi continue.
            </p>
          )}
          <button type="button" className="button button-block" onClick={() => run(main.action)} disabled={drive.submitting}>
            {drive.submitting ? 'Envoi en cours…' : main.label}
          </button>
        </div>
      )}
      {ride.status === 'accepted' && (
        <ConfirmButton
          label="Je ne peux plus faire cette course"
          question="Voulez-vous vraiment vous désister ?"
          details={<p>La course sera proposée aux autres chauffeurs. Le passager n'aura rien à refaire.</p>}
          confirmLabel="Oui, me désister"
          keepLabel="Non, je la garde"
          submitting={release.submitting}
          error={release.error}
          onConfirm={giveUp}
        />
      )}
    </>
  );
}
