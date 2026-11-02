import { useCallback, useState } from 'react';

import { searchPlaces, type Place } from '../api/places';
import { errorMessage } from '../lib/errorMessage';
import { fieldErrors } from '../lib/fieldErrors';

/** One search per tap on "Chercher": on 2G, each search is a round trip. */
export function usePlaceSearch() {
  const [places, setPlaces] = useState<Place[] | null>(null);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (text: string, communeId: number) => {
    setSearching(true);
    setError(null);
    try {
      setPlaces(await searchPlaces(text, communeId));
    } catch (caught) {
      setPlaces(null);
      // A text too short comes back as a field error: its own message is clearer.
      setError(fieldErrors(caught).search ?? errorMessage(caught));
    } finally {
      setSearching(false);
    }
  }, []);

  const clear = useCallback(() => {
    setPlaces(null);
    setError(null);
  }, []);

  return { places, searching, error, search, clear };
}
