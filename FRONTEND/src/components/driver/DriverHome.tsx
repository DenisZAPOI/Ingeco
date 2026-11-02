import { Link } from 'react-router-dom';

import { useUpcomingRides } from '../../hooks/useRides';
import { DRIVER_RIDES_PATH, EARNINGS_PATH } from '../../lib/paths';
import { RideCard } from '../rides/RideCard';
import { ArrowRightIcon, CarIcon, TicketIcon } from '../ui/icons';
import { AvailabilityToggle } from './AvailabilityToggle';

/** The driver's home: online or offline, their next ride, the rides offered. */
export function DriverHome() {
  const upcoming = useUpcomingRides();
  const next = upcoming.data?.items[0];

  return (
    <>
      <AvailabilityToggle />
      {upcoming.error && (
        <p className="note">
          Votre prochaine course n'a pas pu être chargée.{' '}
          <button type="button" className="link-button" onClick={upcoming.retry}>
            Réessayer
          </button>
        </p>
      )}
      {next && (
        <>
          <h2>Votre prochaine course</h2>
          <RideCard ride={next} forDriver />
        </>
      )}
      <div className="stack">
        <Link to={DRIVER_RIDES_PATH} className="action-card action-card-primary">
          <span className="icon-chip icon-chip-sun">
            <CarIcon />
          </span>
          <span className="action-card-text">
            <span className="action-card-title">Courses</span>
            <span className="action-card-hint">Proposées, programmées et les vôtres</span>
          </span>
          <ArrowRightIcon className="action-card-arrow" />
        </Link>
        <Link to={EARNINGS_PATH} className="action-card">
          <span className="icon-chip">
            <TicketIcon />
          </span>
          <span className="action-card-text">
            <span className="action-card-title">Mes revenus</span>
            <span className="action-card-hint">Aujourd'hui, cette semaine, ce mois-ci</span>
          </span>
          <ArrowRightIcon className="action-card-arrow" />
        </Link>
      </div>
    </>
  );
}
