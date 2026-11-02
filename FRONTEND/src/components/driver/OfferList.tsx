import { Link } from 'react-router-dom';

import type { Offer, OfferType } from '../../api/drivers';
import { useOffers } from '../../hooks/useDriver';
import { formatDateTime, formatDistance, formatPrice } from '../../lib/format';
import { driverRidePath } from '../../lib/paths';
import { RequestState } from '../ui/RequestState';
import { ArrowRightIcon } from '../ui/icons';

const EMPTY: Record<OfferType, string> = {
  immediate: "Aucune course à prendre près de vous pour l'instant.",
  scheduled: 'Aucune course à prendre plus tard.',
};

/** Rides the driver could take. No real time yet (step 4): "Actualiser" reads them again. */
export function OfferList({ type }: { type: OfferType }) {
  const offers = useOffers(type);
  const items = offers.data?.items ?? [];

  return (
    <RequestState loading={offers.loading} error={offers.error} onRetry={offers.retry}>
      {type === 'immediate' && offers.data && !offers.data.located && (
        <p className="note">Sans votre position, voici les courses de toute la zone.</p>
      )}
      {items.length === 0 ? (
        <p>{EMPTY[type]}</p>
      ) : (
        <ul className="ride-list">
          {items.map((offer) => (
            <li key={offer.ride.id}>
              <OfferCard offer={offer} />
            </li>
          ))}
        </ul>
      )}
      <button type="button" className="button button-block button-secondary" onClick={offers.retry}>
        Actualiser
      </button>
    </RequestState>
  );
}

function OfferCard({ offer }: { offer: Offer }) {
  const { ride, distanceToPickupKm } = offer;
  return (
    <Link to={driverRidePath(ride.id)} state={{ ride }} className="ride-card">
      <span className="ride-card-text">
        <span className="ride-card-when">
          {ride.scheduledAt ? formatDateTime(ride.scheduledAt) : 'Maintenant'}
          {distanceToPickupKm !== null && ` · à ${formatDistance(distanceToPickupKm)}`}
        </span>
        <span>
          {ride.pickup.address}
          <span className="ride-card-to"> vers </span>
          {ride.dropoff.address}
        </span>
        <span className="ride-card-status">
          {formatPrice(ride.priceCents)} · {formatDistance(ride.distanceKm)}
          {ride.needsAccessibleVehicle && <span className="badge">Véhicule adapté</span>}
        </span>
      </span>
      <ArrowRightIcon className="action-card-arrow" />
    </Link>
  );
}
