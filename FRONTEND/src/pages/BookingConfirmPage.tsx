import { useEffect } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';

import type { Purpose, Stop } from '../api/rides';
import { StepHeader } from '../components/booking/StepHeader';
import { TripSummary } from '../components/booking/TripSummary';
import { Form } from '../components/form/Form';
import { RequestState } from '../components/ui/RequestState';
import { useBookingDraft } from '../hooks/useBookingDraft';
import { useBookRide, useEstimate } from '../hooks/useRides';
import { guyanaDateTime } from '../lib/format';
import { BOOKING_PATHS, paymentPath } from '../lib/paths';
import { newRequestId } from '../lib/requestId';

/** Step 4: the price computed by the API, then the booking. */
export function BookingConfirmPage() {
  const { draft } = useBookingDraft();
  const { pickup, dropoff, purpose } = draft;

  if (!pickup || !dropoff || !purpose) {
    return <Navigate to={BOOKING_PATHS.time} replace />;
  }
  return <Confirmation pickup={pickup} dropoff={dropoff} purpose={purpose} />;
}

function Confirmation({ pickup, dropoff, purpose }: { pickup: Stop; dropoff: Stop; purpose: Purpose }) {
  const { draft, setRequestId } = useBookingDraft();
  const estimate = useEstimate(pickup, dropoff);
  const booking = useBookRide();
  const navigate = useNavigate();
  const scheduledAt = draft.when === 'later' ? new Date(guyanaDateTime(draft.day, draft.time)).toISOString() : null;

  // One identifier per booking, kept for every retry: a booking sent twice on
  // a slow network is booked once (the API returns the first one).
  useEffect(() => {
    if (!draft.requestId) setRequestId(newRequestId());
  }, [draft.requestId, setRequestId]);

  async function confirm() {
    if (!draft.requestId) return;
    const ride = await booking.submit({ clientRequestId: draft.requestId, purpose, pickup, dropoff, scheduledAt });
    if (ride) {
      // The ride goes with the navigation: the payment screen needs no call.
      // The draft is emptied there: emptied here, this step would first send
      // back to the start of the booking.
      navigate(paymentPath(ride.id), { replace: true, state: { ride } });
    }
  }

  // A refused time is a field error: its own message says what to do.
  const bookingError = booking.errors.scheduledAt ?? booking.error;

  return (
    <section>
      <StepHeader step={4} title="Votre trajet" />
      <RequestState loading={estimate.loading} error={estimate.error} onRetry={estimate.retry}>
        {estimate.data && (
          <>
            <TripSummary
              pickup={pickup.address}
              dropoff={dropoff.address}
              purpose={purpose}
              scheduledAt={scheduledAt}
              distanceKm={estimate.data.distanceKm}
              priceCents={estimate.data.riderAmountCents}
            />
            <p className="note">Vous payez par carte à l'étape suivante, avant le départ.</p>
            <Form onSubmit={confirm} submitLabel="Réserver ce trajet" submitting={booking.submitting} error={bookingError} />
          </>
        )}
      </RequestState>
      <Link to={BOOKING_PATHS.pickup} className="link-action">
        Modifier le trajet
      </Link>
    </section>
  );
}
