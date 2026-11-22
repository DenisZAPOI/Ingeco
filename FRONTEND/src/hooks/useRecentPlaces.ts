import { fetchRecentPlaces, type Place } from '../api/places';
import { useRequest } from './useRequest';

const NO_PLACES: Place[] = [];

/** The rider's last places. A shortcut only: while it loads, or if it fails,
 *  the step works as before, with the commune and the search. */
export function useRecentPlaces(): Place[] {
  const request = useRequest(fetchRecentPlaces);
  return request.data ?? NO_PLACES;
}
