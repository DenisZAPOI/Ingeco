import { Link } from 'react-router-dom';

import type { Offer, OfferType } from '../../api/drivers';
import { useOffers } from '../../hooks/useDriver';
import { t } from '../../i18n';
import { formatDateTime, formatDistance, formatPrice } from '../../lib/format';
import { driverRidePath } from '../../lib/paths';
import { RequestState } from '../ui/RequestState';
import { ArrowRightIcon } from '../ui/icons';

function emptyMessage(type: OfferType): string {
  return type === 'immediate' ? t('driver.noOfferNow') : t('driver.noOfferLater');
}

/** Rides the driver could take. No real time yet (step 4): "Actualiser" reads them again. */
export function OfferList({ type }: { type: OfferType }) {
  const offers = useOffers(type);
  const items = offers.data?.items ?? [];

  return (
    <RequestState loading={offers.loading} error={offers.error} onRetry={offers.retry}>
      {type === 'immediate' && offers.data && !offers.data.located && (
        <p className="note">{t('driver.wholeZone')}</p>
      )}
      {items.length === 0 ? (
        <p>{emptyMessage(type)}</p>
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
        {t('driver.refresh')}
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
          {ride.scheduledAt ? formatDateTime(ride.scheduledAt) : t('driver.now')}
          {distanceToPickupKm !== null && t('driver.distanceToPickup', { distance: formatDistance(distanceToPickupKm) })}
        </span>
        <span>
          {ride.pickup.address}
          <span className="ride-card-to">{t('driver.to')}</span>
          {ride.dropoff.address}
        </span>
        <span className="ride-card-status">
          {formatPrice(ride.priceCents)} · {formatDistance(ride.distanceKm)}
          {ride.needsAccessibleVehicle && <span className="badge">{t('driver.accessibleBadge')}</span>}
        </span>
      </span>
      <ArrowRightIcon className="action-card-arrow" />
    </Link>
  );
}
