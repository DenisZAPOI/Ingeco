import { useEffect, useState } from 'react';

import { fetchCommunes } from '../api/places';
import { readStoredCommunes, storeCommunes } from '../lib/storedCommunes';
import { useRequest } from './useRequest';

// Confirmed by the API once per opening of the app: the two address steps
// must not cost a round trip each for a list that almost never changes.
let confirmedThisVisit = false;

/** The served communes: the stored list at once, confirmed by the API. */
export function useCommunes() {
  const [stored] = useState(readStoredCommunes);
  const [refresh] = useState(() => !confirmedThisVisit);
  const request = useRequest(fetchCommunes, stored, refresh);

  useEffect(() => {
    if (request.data && !request.loading) {
      storeCommunes(request.data);
    }
  }, [request.data, request.loading]);

  useEffect(() => {
    if (request.data && !request.error) confirmedThisVisit = true;
  }, [request.data, request.error]);

  // A failed confirmation does not hide a list already shown.
  return { ...request, error: request.data ? null : request.error };
}
