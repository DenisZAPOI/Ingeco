import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';

import type { Ride } from '../api/rides';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { TripSummary } from '../components/booking/TripSummary';
import { CancelRide } from '../components/rides/CancelRide';
import { DriverCard } from '../components/rides/DriverCard';
import { RatingForm, RatingSummary } from '../components/rides/RatingForm';
import { RequestState } from '../components/ui/RequestState';
import { CarIcon } from '../components/ui/icons';
import { useRide } from '../hooks/useRides';
import { formatPrice } from '../lib/format';
import { BOOKING_PATHS, RIDES_PATH, paymentPath } from '../lib/paths';
import { STATUS_HEADLINES, canCancel, canRate, canStillPay, expiryReason, isOver, rideDate, rideFromState } from '../lib/ride';
import { draftFromRide, saveBookingDraft } from '../lib/bookingDraft';

/** Where the trip stands, what can still be done (pay, cancel, rate).
 *  The map and the driver come with step 4 (real time). */
export function RidePage() {
  const id = Number(useParams().id);
  const location = useLocation();
  const navigate = useNavigate();
  const ride = useRide(id, rideFromState(location.state, id));

  // The new state also replaces the one kept in the history: coming back
  // here later shows the trip as it is now, not as it was.
  function update(changed: Ride) {
    ride.setData(changed);
    navigate(location.pathname, { replace: true, state: { ride: changed } });
  }

  return (
    <section>
      <PageHero title="Mon trajet" />
      <PageSheet>
        <RequestState loading={ride.loading} error={ride.error} onRetry={ride.retry}>
          {ride.data && <RideStatus ride={ride.data} onRefresh={ride.retry} onChange={update} />}
        </RequestState>
        <Link to={RIDES_PATH} className="link-action">
          Voir mes trajets
        </Link>
      </PageSheet>
    </section>
  );
}

type RideStatusProps = {
  ride: Ride;
  onRefresh: () => void;
  onChange: (ride: Ride) => void;
};

// A driver is on the way, or the rider is on board.
const UNDER_WAY: readonly Ride['status'][] = ['accepted', 'in_progress'];

function RideStatus({ ride, onRefresh, onChange }: RideStatusProps) {
  return (
    <>
      <p role="status" className="status">
        <span className="icon-chip icon-chip-sun">
          <CarIcon />
        </span>
        {STATUS_HEADLINES[ride.status]}
      </p>
      {canStillPay(ride) && (
        <Link to={paymentPath(ride.id)} state={{ ride }} className="button button-block">
          Payer {formatPrice(ride.riderAmountCents)}
        </Link>
      )}
      {ride.status === 'pending' && (
        <>
          <p>Votre paiement est bien reçu. Revenez sur cette page pour savoir quand un chauffeur a accepté.</p>
          <button type="button" className="button button-block button-secondary" onClick={onRefresh}>
            Actualiser
          </button>
        </>
      )}
      {ride.driver && UNDER_WAY.includes(ride.status) && <DriverCard driver={ride.driver} />}
      {UNDER_WAY.includes(ride.status) && (
        // No real time yet (step 4): the driver may have started meanwhile.
        <button type="button" className="button button-block button-secondary" onClick={onRefresh}>
          Actualiser
        </button>
      )}
      {ride.status === 'expired' && <p>{expiryReason(ride)}</p>}
      {ride.paymentStatus === 'refunded' && (
        <p className="alert alert-info">Vous êtes remboursé de {formatPrice(ride.riderAmountCents)}.</p>
      )}
      {canRate(ride) && (
        <>
          <h2>Votre avis</h2>
          <RatingForm ride={ride} onRated={onChange} />
          <p className="note">Vous pouvez aussi noter ce trajet plus tard, depuis « Mes trajets ».</p>
        </>
      )}
      {ride.rating && (
        <>
          <h2>Votre avis</h2>
          <RatingSummary score={ride.rating.score} comment={ride.rating.comment} />
        </>
      )}
      <h2>Détails</h2>
      <TripSummary
        pickup={ride.pickup.address}
        dropoff={ride.dropoff.address}
        purpose={ride.purpose}
        // Once over, "Dès que possible" would mean nothing: the day it was.
        scheduledAt={isOver(ride) ? rideDate(ride) : ride.scheduledAt}
        distanceKm={ride.distanceKm}
        priceCents={ride.priceCents}
      />
      {canCancel(ride) && <CancelRide ride={ride} onCancelled={onChange} />}
      {ride.status === 'expired' && <RebookButton ride={ride} />}
    </>
  );
}

/** The same trip again, after an expiry: only the time is left to choose. */
function RebookButton({ ride }: { ride: Ride }) {
  const navigate = useNavigate();

  function rebook() {
    saveBookingDraft(draftFromRide(ride));
    navigate(BOOKING_PATHS.time);
  }

  return (
    <button type="button" className="button button-block" onClick={rebook}>
      Réserver à nouveau ce trajet
    </button>
  );
}
