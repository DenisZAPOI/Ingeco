import type { Purpose } from '../../api/rides';
import { formatDateTime, formatDistance, formatPrice } from '../../lib/format';
import { PURPOSE_LABELS } from '../../lib/ride';

type TripSummaryProps = {
  pickup: string;
  dropoff: string;
  purpose: Purpose;
  /** ISO date of a scheduled trip; null to leave as soon as possible. */
  scheduledAt: string | null;
  distanceKm?: number;
  priceCents?: number;
};

/** The trip in a few lines: confirmation, payment, follow-up. */
export function TripSummary({ pickup, dropoff, purpose, scheduledAt, distanceKm, priceCents }: TripSummaryProps) {
  return (
    <dl className="panel summary">
      <dt>Départ</dt>
      <dd>{pickup}</dd>
      <dt>Arrivée</dt>
      <dd>{dropoff}</dd>
      <dt>Quand</dt>
      <dd>{scheduledAt ? formatDateTime(scheduledAt) : 'Dès que possible'}</dd>
      <dt>Motif</dt>
      <dd>{PURPOSE_LABELS[purpose]}</dd>
      {distanceKm !== undefined && (
        <>
          <dt>Distance</dt>
          <dd>{formatDistance(distanceKm)}</dd>
        </>
      )}
      {priceCents !== undefined && (
        <>
          <dt>Prix</dt>
          <dd className="summary-price">{formatPrice(priceCents)}</dd>
        </>
      )}
    </dl>
  );
}
