import { Link } from 'react-router-dom';

import type { Ride } from '../../api/rides';
import { formatDateTime } from '../../lib/format';
import { ridePath } from '../../lib/paths';
import { STATUS_LABELS, canRate, rideDate } from '../../lib/ride';
import { ArrowRightIcon } from '../ui/icons';

/** A trip in a list: when, where, its state. Opens the trip page without a new call. */
export function RideCard({ ride }: { ride: Ride }) {
  return (
    <Link to={ridePath(ride.id)} state={{ ride }} className="ride-card">
      <span className="ride-card-text">
        <span className="ride-card-when">{formatDateTime(rideDate(ride))}</span>
        <span>
          {ride.pickup.address}
          <span className="ride-card-to"> vers </span>
          {ride.dropoff.address}
        </span>
        <span className="ride-card-status">
          {STATUS_LABELS[ride.status]}
          {canRate(ride) && <span className="badge">À noter</span>}
        </span>
      </span>
      <ArrowRightIcon className="action-card-arrow" />
    </Link>
  );
}

/** Trips one under the other. */
export function RideList({ rides }: { rides: Ride[] }) {
  return (
    <ul className="ride-list">
      {rides.map((ride) => (
        <li key={ride.id}>
          <RideCard ride={ride} />
        </li>
      ))}
    </ul>
  );
}
