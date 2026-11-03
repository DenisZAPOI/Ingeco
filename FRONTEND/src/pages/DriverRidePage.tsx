import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';

import type { Ride } from '../api/rides';
import { TripSummary } from '../components/booking/TripSummary';
import { DriverRideActions } from '../components/driver/DriverRideActions';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { RequestState } from '../components/ui/RequestState';
import { CarIcon } from '../components/ui/icons';
import { useRide } from '../hooks/useRides';
import { t } from '../i18n';
import { driverStatusHeadline } from '../lib/driver';
import { DRIVER_RIDES_PATH } from '../lib/paths';
import { isOver, rideDate, rideFromState } from '../lib/ride';

/** A ride seen by the driver: the offer, then the ride they hold. */
export function DriverRidePage() {
  const id = Number(useParams().id);
  const location = useLocation();
  const navigate = useNavigate();
  const ride = useRide(id, rideFromState(location.state, id));

  // The new state also replaces the one kept in the history (see RidePage).
  function update(changed: Ride) {
    ride.setData(changed);
    navigate(location.pathname, { replace: true, state: { ride: changed } });
  }

  return (
    <section>
      <PageHero title={t('driver.rideTitle')} />
      <PageSheet>
        <RequestState loading={ride.loading} error={ride.error} onRetry={ride.retry}>
          {ride.data && <DriverRide ride={ride.data} onRefresh={ride.retry} onChange={update} />}
        </RequestState>
        <Link to={DRIVER_RIDES_PATH} className="link-action">
          {t('driver.seeRides')}
        </Link>
      </PageSheet>
    </section>
  );
}

type DriverRideProps = {
  ride: Ride;
  onRefresh: () => void;
  onChange: (ride: Ride) => void;
};

function DriverRide({ ride, onRefresh, onChange }: DriverRideProps) {
  return (
    <>
      <p role="status" className="status">
        <span className="icon-chip icon-chip-sun">
          <CarIcon />
        </span>
        {driverStatusHeadline(ride.status)}
      </p>
      {ride.needsAccessibleVehicle && (
        <p className="alert alert-info">{t('driver.needsAccessible')}</p>
      )}
      <DriverRideActions ride={ride} onChange={onChange} />
      <h2>{t('driver.details')}</h2>
      <TripSummary
        pickup={ride.pickup.address}
        dropoff={ride.dropoff.address}
        purpose={ride.purpose}
        scheduledAt={isOver(ride) ? rideDate(ride) : ride.scheduledAt}
        distanceKm={ride.distanceKm}
        priceCents={ride.priceCents}
      />
      {!isOver(ride) && (
        // No real time yet (step 4): the rider may have cancelled meanwhile.
        <button type="button" className="button button-block button-secondary" onClick={onRefresh}>
          {t('driver.refresh')}
        </button>
      )}
    </>
  );
}
