import { useEffect } from 'react';
import { Link, Navigate, useLocation, useNavigate, useParams } from 'react-router-dom';

import type { Ride } from '../api/rides';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { TripSummary } from '../components/booking/TripSummary';
import { Form } from '../components/form/Form';
import { RequestState } from '../components/ui/RequestState';
import { usePayRide, useRide } from '../hooks/useRides';
import { t } from '../i18n';
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
      <PageHero title={t('payment.title')} />
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
          {t('payment.tooLate')}
        </p>
        <Link to={BOOKING_PATHS.pickup} className="button button-block">
          {t('payment.bookAgain')}
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
        {t('payment.toPay')} <strong>{formatPrice(ride.riderAmountCents)}</strong>
      </p>
      <p>{t('payment.payBefore', { time: formatTime(ride.expiresAt) })}</p>
      <TripSummary
        pickup={ride.pickup.address}
        dropoff={ride.dropoff.address}
        purpose={ride.purpose}
        scheduledAt={ride.scheduledAt}
      />
      <p className="alert alert-info">{t('payment.test')}</p>
      <Form
        onSubmit={pay}
        submitLabel={t('ride.pay', { amount: formatPrice(ride.riderAmountCents) })}
        submitting={payment.submitting}
        error={payment.error}
      />
    </>
  );
}
