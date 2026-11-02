import { useEffect } from 'react';
import { Link, Navigate, useLocation, useNavigate, useParams } from 'react-router-dom';

import type { Ride } from '../api/rides';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { TripSummary } from '../components/booking/TripSummary';
import { Form } from '../components/form/Form';
import { RequestState } from '../components/ui/RequestState';
import { usePayRide, useRide } from '../hooks/useRides';
import { saveBookingDraft } from '../lib/bookingDraft';
import { formatPrice, formatTime } from '../lib/format';
import { BOOKING_PATHS, ridePath } from '../lib/paths';
import { canStillPay, rideFromState } from '../lib/ride';

/** Simulated card payment of the rider's share (no real money, H10). */
export function RidePaymentPage() {
  const id = Number(useParams().id);
  const ride = useRide(id, rideFromState(useLocation().state, id));

  // The booking is made: the next one starts empty.
  useEffect(() => saveBookingDraft(null), []);

  return (
    <section>
      <PageHero title="Payer le trajet" />
      <PageSheet>
        <RequestState loading={ride.loading} error={ride.error} onRetry={ride.retry}>
          {ride.data && <Payment ride={ride.data} />}
        </RequestState>
      </PageSheet>
    </section>
  );
}

function Payment({ ride }: { ride: Ride }) {
  const payment = usePayRide();
  const navigate = useNavigate();

  // Already paid, cancelled…: the trip page says where it stands.
  if (ride.status !== 'awaiting_payment') {
    return <Navigate to={ridePath(ride.id)} replace state={{ ride }} />;
  }

  if (!canStillPay(ride)) {
    return (
      <>
        <p role="alert" className="alert alert-error">
          Le délai de 15 minutes pour payer est dépassé. Cette réservation n'est plus valable.
        </p>
        <Link to={BOOKING_PATHS.pickup} className="button button-block">
          Refaire une réservation
        </Link>
      </>
    );
  }

  async function pay() {
    const paid = await payment.submit(ride.id);
    if (paid) navigate(ridePath(paid.id), { replace: true, state: { ride: paid } });
  }

  return (
    <>
      <p className="lead">
        À payer : <strong>{formatPrice(ride.riderAmountCents)}</strong>
      </p>
      <p>Payez avant {formatTime(ride.expiresAt)}. Après, la réservation n'est plus valable.</p>
      <TripSummary
        pickup={ride.pickup.address}
        dropoff={ride.dropoff.address}
        purpose={ride.purpose}
        scheduledAt={ride.scheduledAt}
      />
      <p className="alert alert-info">Paiement de test : aucune carte n'est débitée.</p>
      <Form
        onSubmit={pay}
        submitLabel={`Payer ${formatPrice(ride.riderAmountCents)}`}
        submitting={payment.submitting}
        error={payment.error}
      />
    </>
  );
}
