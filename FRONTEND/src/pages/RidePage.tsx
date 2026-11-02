import { Link, useLocation, useParams } from 'react-router-dom';

import type { Ride } from '../api/rides';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { TripSummary } from '../components/booking/TripSummary';
import { RequestState } from '../components/ui/RequestState';
import { CarIcon } from '../components/ui/icons';
import { useRide } from '../hooks/useRides';
import { formatPrice } from '../lib/format';
import { paymentPath } from '../lib/paths';
import { STATUS_HEADLINES, canStillPay, rideFromState } from '../lib/ride';

/** Where the trip stands. The map and the driver come with step 4 (real time). */
export function RidePage() {
  const id = Number(useParams().id);
  const ride = useRide(id, rideFromState(useLocation().state, id));

  return (
    <section>
      <PageHero title="Mon trajet" />
      <PageSheet>
        <RequestState loading={ride.loading} error={ride.error} onRetry={ride.retry}>
          {ride.data && <RideStatus ride={ride.data} onRefresh={ride.retry} />}
        </RequestState>
        <Link to="/" className="link-action">
          Retour à l'accueil
        </Link>
      </PageSheet>
    </section>
  );
}

function RideStatus({ ride, onRefresh }: { ride: Ride; onRefresh: () => void }) {
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
      <h2>Détails</h2>
      <TripSummary
        pickup={ride.pickup.address}
        dropoff={ride.dropoff.address}
        purpose={ride.purpose}
        scheduledAt={ride.scheduledAt}
        distanceKm={ride.distanceKm}
        priceCents={ride.priceCents}
      />
    </>
  );
}
