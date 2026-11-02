import { useUpcomingRides } from '../../hooks/useRides';
import { RideCard } from './RideCard';

/** The rider's next trip, first on the home screen. Nothing while it loads:
 *  the home screen stays usable without it. */
export function NextRide() {
  const upcoming = useUpcomingRides();
  const next = upcoming.data?.items[0];

  if (upcoming.error) {
    return (
      <p className="note">
        Votre prochain trajet n'a pas pu être chargé.{' '}
        <button type="button" className="link-button" onClick={upcoming.retry}>
          Réessayer
        </button>
      </p>
    );
  }
  if (!next) return null;
  return (
    <>
      <h2>Votre prochain trajet</h2>
      <RideCard ride={next} />
    </>
  );
}
