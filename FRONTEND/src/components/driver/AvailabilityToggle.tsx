import { useSession } from '../../hooks/useSession';
import { useSetAvailability } from '../../hooks/useDriver';
import { useDriverLocation } from '../../hooks/useDriverLocation';
import type { LocationStatus } from '../../context/driverLocationContext';

const LOCATION_NOTES: Partial<Record<LocationStatus, string>> = {
  waiting: 'Recherche de votre position…',
  denied:
    'Position refusée : vous voyez les courses de toute la zone, sans la distance. ' +
    'Pour voir les plus proches, autorisez la position pour cette application dans les réglages du téléphone.',
  unavailable: 'Votre position est introuvable pour le moment : vous voyez les courses de toute la zone.',
};

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

  const label = online ? 'Je ne suis plus disponible' : 'Je suis disponible';
  const note = LOCATION_NOTES[location];
  return (
    <div className="availability">
      <p role="status" className="status">
        <span className={online ? 'availability-dot availability-dot-on' : 'availability-dot'} aria-hidden="true" />
        {online ? 'Vous êtes disponible' : 'Vous êtes hors ligne'}
      </p>
      <p className="note">
        {online
          ? 'Vous recevez les courses proposées. Votre position est partagée tant que vous êtes disponible.'
          : 'Vous ne recevez pas de course. Vos courses déjà acceptées restent les vôtres.'}
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
        {availability.submitting ? 'Envoi en cours…' : label}
      </button>
    </div>
  );
}
