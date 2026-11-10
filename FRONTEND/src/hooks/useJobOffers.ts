import { useCallback, useEffect, useState } from 'react';

import { fetchJobOffer, fetchJobOffers, type JobOffer } from '../api/jobs';
import { readStoredJobOffers, storeJobOffers } from '../lib/jobs';
import { useRequest } from './useRequest';

/** Every offer online: the list kept on the phone at once, confirmed by the API. */
export function useJobOffers() {
  const [stored] = useState(readStoredJobOffers);
  const request = useRequest(fetchJobOffers, stored, true);

  useEffect(() => {
    if (request.data && !request.loading && !request.error) {
      storeJobOffers(request.data);
    }
  }, [request.data, request.loading, request.error]);

  // A failed confirmation does not hide a list already shown.
  return { ...request, error: request.data ? null : request.error };
}

/** One offer: the one the list handed over (or kept on the phone) at once,
 *  confirmed by the API, which also says if it is no longer online. */
export function useJobOffer(id: number, known: JobOffer | null) {
  const [first] = useState(() => known ?? readStoredJobOffers()?.find((offer) => offer.id === id) ?? null);
  const load = useCallback(() => fetchJobOffer(id), [id]);
  return useRequest(load, first, true);
}
