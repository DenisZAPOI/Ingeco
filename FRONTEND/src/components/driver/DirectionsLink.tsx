import { directionsUrl, type LatLng } from '../../lib/geo';
import { ArrowRightIcon } from '../ui/icons';

/** Opens the phone's GPS app towards a stop (UC25): no route computed here. */
export function DirectionsLink({ label, to }: { label: string; to: LatLng }) {
  return (
    <a href={directionsUrl(to)} target="_blank" rel="noopener noreferrer" className="button button-block button-secondary">
      {label}
      <ArrowRightIcon className="button-icon" />
    </a>
  );
}
