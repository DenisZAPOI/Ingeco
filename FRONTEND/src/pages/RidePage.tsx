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
import { t } from '../i18n';
import { formatPrice } from '../lib/format';
import { BOOKING_PATHS, RIDES_PATH, paymentPath } from '../lib/paths';
import { canCancel, canRate, canStillPay, expiryReason, isOver, rideDate, rideFromState, statusHeadline } from '../lib/ride';
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
      <PageHero title={t('ride.title')} />
      <PageSheet>
        <RequestState loading={ride.loading} error={ride.error} onRetry={ride.retry}>
          {ride.data && <RideStatus ride={ride.data} onRefresh={ride.retry} onChange={update} />}
        </RequestState>
        <Link to={RIDES_PATH} className="link-action">
          {t('ride.seeMyRides')}
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
        {statusHeadline(ride.status)}
      </p>
      {canStillPay(ride) && (
        <Link to={paymentPath(ride.id)} state={{ ride }} className="button button-block">
          {t('ride.pay', { amount: formatPrice(ride.riderAmountCents) })}
        </Link>
      )}
      {ride.status === 'pending' && (
        <>
          <p>{t(ride.paymentStatus === 'not_required' ? 'ride.freeWaiting' : 'ride.paidWaiting')}</p>
          <button type="button" className="button button-block button-secondary" onClick={onRefresh}>
            {t('ride.refresh')}
          </button>
        </>
      )}
      {ride.driver && UNDER_WAY.includes(ride.status) && <DriverCard driver={ride.driver} />}
      {UNDER_WAY.includes(ride.status) && (
        // No real time yet (step 4): the driver may have started meanwhile.
        <button type="button" className="button button-block button-secondary" onClick={onRefresh}>
          {t('ride.refresh')}
        </button>
      )}
      {ride.status === 'expired' && <p>{expiryReason(ride)}</p>}
      {ride.paymentStatus === 'refunded' && (
        <p className="alert alert-info">{t('ride.refunded', { amount: formatPrice(ride.riderAmountCents) })}</p>
      )}
      {canRate(ride) && (
        <>
          <h2>{t('ride.yourRating')}</h2>
          <RatingForm ride={ride} onRated={onChange} />
          <p className="note">{t('ride.rateLater')}</p>
        </>
      )}
      {ride.rating && (
        <>
          <h2>{t('ride.yourRating')}</h2>
          <RatingSummary score={ride.rating.score} comment={ride.rating.comment} />
        </>
      )}
      <h2>{t('ride.details')}</h2>
      <TripSummary
        pickup={ride.pickup.address}
        dropoff={ride.dropoff.address}
        purpose={ride.purpose}
        // Once over, "Dès que possible" would mean nothing: the day it was.
        scheduledAt={isOver(ride) ? rideDate(ride) : ride.scheduledAt}
        distanceKm={ride.distanceKm}
        price={{ totalCents: ride.priceCents, riderCents: ride.riderAmountCents }}
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
      {t('ride.rebook')}
    </button>
  );
}
