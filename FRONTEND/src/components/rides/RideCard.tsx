import { Link } from 'react-router-dom';

import type { Ride } from '../../api/rides';
import { DRIVER_STATUS_LABELS } from '../../lib/driver';
import { formatDateTime } from '../../lib/format';
import { driverRidePath, ridePath } from '../../lib/paths';
import { STATUS_LABELS, canRate, rideDate } from '../../lib/ride';
import { ArrowRightIcon } from '../ui/icons';

type RideCardProps = {
  ride: Ride;
  /** The driver's card: their words, their ride page, no "À noter". */
  forDriver?: boolean;
};

/** A trip in a list: when, where, its state. Opens its page without a new call. */
export function RideCard({ ride, forDriver = false }: RideCardProps) {
  return (
    <Link to={forDriver ? driverRidePath(ride.id) : ridePath(ride.id)} state={{ ride }} className="ride-card">
      <span className="ride-card-text">
        <span className="ride-card-when">{formatDateTime(rideDate(ride))}</span>
        <span>
          {ride.pickup.address}
          <span className="ride-card-to"> vers </span>
          {ride.dropoff.address}
        </span>
        <span className="ride-card-status">
          {(forDriver ? DRIVER_STATUS_LABELS : STATUS_LABELS)[ride.status]}
          {!forDriver && canRate(ride) && <span className="badge">À noter</span>}
        </span>
      </span>
      <ArrowRightIcon className="action-card-arrow" />
    </Link>
  );
}

/** Trips one under the other. */
export function RideList({ rides, forDriver = false }: { rides: Ride[]; forDriver?: boolean }) {
  return (
    <ul className="ride-list">
      {rides.map((ride) => (
        <li key={ride.id}>
          <RideCard ride={ride} forDriver={forDriver} />
        </li>
      ))}
    </ul>
  );
}
