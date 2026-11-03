import type { Purpose } from '../../api/rides';
import { t } from '../../i18n';
import { formatDateTime, formatDistance, formatPrice } from '../../lib/format';
import { purposeLabel } from '../../lib/ride';

type TripSummaryProps = {
  pickup: string;
  dropoff: string;
  purpose: Purpose;
  /** ISO date the trip leaves (scheduled, or past); null to leave as soon as possible. */
  scheduledAt: string | null;
  distanceKm?: number;
  priceCents?: number;
};

/** The trip in a few lines: confirmation, payment, follow-up. */
export function TripSummary({ pickup, dropoff, purpose, scheduledAt, distanceKm, priceCents }: TripSummaryProps) {
  return (
    <dl className="panel summary">
      <dt>{t('ride.pickup')}</dt>
      <dd>{pickup}</dd>
      <dt>{t('ride.dropoff')}</dt>
      <dd>{dropoff}</dd>
      <dt>{t('ride.when')}</dt>
      <dd>{scheduledAt ? formatDateTime(scheduledAt) : t('ride.asap')}</dd>
      <dt>{t('ride.purpose')}</dt>
      <dd>{purposeLabel(purpose)}</dd>
      {distanceKm !== undefined && (
        <>
          <dt>{t('ride.distance')}</dt>
          <dd>{formatDistance(distanceKm)}</dd>
        </>
      )}
      {priceCents !== undefined && (
        <>
          <dt>{t('ride.price')}</dt>
          <dd className="summary-price">{formatPrice(priceCents)}</dd>
        </>
      )}
    </dl>
  );
}
