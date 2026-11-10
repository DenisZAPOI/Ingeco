import { useState } from 'react';

import type { Ride } from '../../api/rides';
import { t } from '../../i18n';
import { formatScore } from '../../lib/format';
import { formatPhone } from '../../lib/phone';
import { PhoneIcon } from '../ui/icons';

type Driver = NonNullable<Ride['driver']>;

// Shown at half the size it is taken at (lib/photo.ts): sharp on dense screens.
const PHOTO_SIZE = 96;

/** Who comes to pick the rider up: their face, first name, vehicle and
 *  rating. The photo loads on its own, after the text: on 2G the first name
 *  and the plate are already there to read (about 15 KB, half a second). */
export function DriverCard({ driver, photoUrl }: { driver: Driver; photoUrl: string | null }) {
  // A photo that cannot load (network cut) leaves no broken image behind.
  const [photoFailed, setPhotoFailed] = useState(false);

  return (
    <div className="panel">
      <div className="driver-card-head">
        {photoUrl && !photoFailed && (
          <img
            src={photoUrl}
            alt={t('ride.driverPhotoAlt', { name: driver.firstName })}
            className="driver-photo driver-photo-small"
            width={PHOTO_SIZE}
            height={PHOTO_SIZE}
            onError={() => setPhotoFailed(true)}
          />
        )}
        <p className="driver-card-name">
          <span className="note">{t('ride.yourDriver')}</span>
          <strong>{driver.firstName}</strong>
        </p>
      </div>
      <dl className="summary">
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
