import { useCallback, useEffect, useState } from 'react';

import { fetchHelpService, fetchHelpServices, type HelpService } from '../api/helpServices';
import { readStoredHelpServices, storeHelpServices } from '../lib/helpServices';
import { useRequest } from './useRequest';

/** Every help service: the list kept on the phone at once, confirmed by the API. */
export function useHelpServices() {
  const [stored] = useState(readStoredHelpServices);
  const request = useRequest(fetchHelpServices, stored, true);

  useEffect(() => {
    if (request.data && !request.loading && !request.error) {
      storeHelpServices(request.data);
    }
  }, [request.data, request.loading, request.error]);

  // A failed confirmation does not hide a list already shown.
  return { ...request, error: request.data ? null : request.error };
}

/** One service: the one the list handed over (or kept on the phone) at once,
 *  confirmed by the API. */
export function useHelpService(id: number, known: HelpService | null) {
  const [first] = useState(() => known ?? readStoredHelpServices()?.find((service) => service.id === id) ?? null);
  const load = useCallback(() => fetchHelpService(id), [id]);
  return useRequest(load, first, true);
}
