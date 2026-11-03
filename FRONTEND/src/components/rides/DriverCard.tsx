import type { Ride } from '../../api/rides';
import { t } from '../../i18n';
import { formatScore } from '../../lib/format';
import { formatPhone } from '../../lib/phone';
import { PhoneIcon } from '../ui/icons';

type Driver = NonNullable<Ride['driver']>;

/** Who comes to pick the rider up. The photo and the map come with step 4. */
export function DriverCard({ driver }: { driver: Driver }) {
  return (
    <div className="panel">
      <dl className="summary">
        <dt>{t('ride.yourDriver')}</dt>
        <dd>{driver.firstName}</dd>
        <dt>{t('ride.vehicle')}</dt>
        <dd>
          {driver.vehicle.model}, {driver.vehicle.plate}
          {driver.vehicle.isAccessible && t('ride.accessibleVehicle')}
        </dd>
        <dt>{t('ride.driverScore')}</dt>
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
      {t('ride.call', { name, phone: formatPhone(phone) })}
    </a>
  );
}
