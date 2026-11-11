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
  /** The price of the trip, and the rider's share of it. */
  price?: { totalCents: number; riderCents: number };
};

/** The trip in a few lines: confirmation, payment, follow-up. */
export function TripSummary({ pickup, dropoff, purpose, scheduledAt, distanceKm, price }: TripSummaryProps) {
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
      {price && price.riderCents === price.totalCents && (
        <>
          <dt>{t('ride.price')}</dt>
          <dd className="summary-price">{formatPrice(price.totalCents)}</dd>
        </>
      )}
      {/* Covered in whole or in part: the value of the trip, then what is left
          to pay, the line that matters (reste à payer, cahier des charges §7.4). */}
      {price && price.riderCents < price.totalCents && (
        <>
          <dt>{t('ride.price')}</dt>
          <dd>{formatPrice(price.totalCents)}</dd>
          <dt>{t('ride.covered')}</dt>
          <dd>{formatPrice(price.totalCents - price.riderCents)}</dd>
          <dt>{t('ride.toPay')}</dt>
          <dd className="summary-price">{formatPrice(price.riderCents)}</dd>
        </>
      )}
    </dl>
  );
}
