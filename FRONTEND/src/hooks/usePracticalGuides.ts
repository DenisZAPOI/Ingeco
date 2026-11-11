import { useCallback, useEffect, useState } from 'react';

import { fetchPracticalGuide, fetchPracticalGuides, type PracticalGuide } from '../api/practicalGuides';
import { readStoredGuides, storeGuides } from '../lib/practicalGuides';
import { useRequest } from './useRequest';

/** Every guide: the list kept on the phone at once, confirmed by the API. */
export function usePracticalGuides() {
  const [stored] = useState(readStoredGuides);
  const request = useRequest(fetchPracticalGuides, stored, true);

  useEffect(() => {
    if (request.data && !request.loading && !request.error) {
      storeGuides(request.data);
    }
  }, [request.data, request.loading, request.error]);

  // A failed confirmation does not hide a list already shown.
  return { ...request, error: request.data ? null : request.error };
}

/** One guide: the one handed over (or kept on the phone) at once, confirmed by the API. */
export function usePracticalGuide(id: number, known: PracticalGuide | null) {
  const [first] = useState(() => known ?? readStoredGuides()?.find((guide) => guide.id === id) ?? null);
  const load = useCallback(() => fetchPracticalGuide(id), [id]);
  return useRequest(load, first, true);
}
