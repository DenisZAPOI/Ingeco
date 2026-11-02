import type { Ride } from '../../api/rides';
import { formatScore } from '../../lib/format';
import { formatPhone } from '../../lib/phone';
import { PhoneIcon } from '../ui/icons';

type Driver = NonNullable<Ride['driver']>;

/** Who comes to pick the rider up. The photo and the map come with step 4. */
export function DriverCard({ driver }: { driver: Driver }) {
  return (
    <div className="panel">
      <dl className="summary">
        <dt>Votre chauffeur</dt>
        <dd>{driver.firstName}</dd>
        <dt>Véhicule</dt>
        <dd>
          {driver.vehicle.model}, {driver.vehicle.plate}
          {driver.vehicle.isAccessible && ' (adapté au fauteuil roulant)'}
        </dd>
        <dt>Note des passagers</dt>
        <dd>{formatScore(driver.averageScore)}</dd>
      </dl>
      {driver.phone && <CallLink name={driver.firstName} phone={driver.phone} />}
    </div>
  );
}

/** A large "Appeler …" link: opens the phone's dialler. */
export function CallLink({ name, phone }: { name: string; phone: string }) {
  return (
    <a href={`tel:${phone}`} className="button button-block button-secondary">
      <PhoneIcon className="button-icon" />
      Appeler {name} ({formatPhone(phone)})
    </a>
  );
}
