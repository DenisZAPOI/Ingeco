import { directionsUrl, mapUrl, type LatLng } from '../../lib/geo';
import { ArrowRightIcon } from '../ui/icons';

// Android hands geo: links to the GPS app the driver chose; elsewhere they may open nothing.
const answersGeoLinks = /Android/i.test(navigator.userAgent);

/** Opens the phone's GPS app towards a stop (UC25), or a map: no route computed here. */
export function DirectionsLink({ label, to }: { label: string; to: LatLng }) {
  const href = answersGeoLinks ? directionsUrl(to) : mapUrl(to);
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className="button button-block button-secondary">
      {label}
      <ArrowRightIcon className="button-icon" />
    </a>
  );
}
