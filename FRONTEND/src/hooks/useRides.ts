import { useCallback, useState } from 'react';

import {
  bookRide,
  cancelRide,
  estimateRide,
  fetchPastRides,
  fetchRide,
  fetchUpcomingRides,
  payRide,
  rateRide,
  type Booking,
  type RatingBody,
  type Ride,
  type Stop,
} from '../api/rides';
import { errorMessage } from '../lib/errorMessage';
import { useRequest } from './useRequest';
import { useSubmit } from './useSubmit';

export function useEstimate(pickup: Stop, dropoff: Stop) {
  return useRequest(useCallback(() => estimateRide(pickup, dropoff), [pickup, dropoff]));
}

/** `known`: the ride handed over by the previous screen, shown without a call. */
export function useRide(id: number, known: Ride | null) {
  return useRequest(useCallback(() => fetchRide(id), [id]), known);
}

export function useBookRide() {
  return useSubmit(useCallback((booking: Booking) => bookRide(booking), []));
}

export function usePayRide() {
  return useSubmit(useCallback((id: number) => payRide(id), []));
}

export function useCancelRide() {
  return useSubmit(useCallback((id: number) => cancelRide(id), []));
}

export function useRateRide(id: number) {
  return useSubmit(useCallback((rating: RatingBody) => rateRide(id, rating), [id]));
}

export function useUpcomingRides() {
  return useRequest(fetchUpcomingRides);
}

const firstPastPage = () => fetchPastRides(null);

/** Finished rides, page after page: the first one on arrival, the next ones on "Voir plus". */
export function usePastRides() {
  const firstPage = useRequest(firstPastPage);
  const [morePages, setMorePages] = useState<{ items: Ride[]; nextCursor: string | null } | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const [moreError, setMoreError] = useState<string | null>(null);

  const rides = [...(firstPage.data?.items ?? []), ...(morePages?.items ?? [])];
  const nextCursor = morePages ? morePages.nextCursor : (firstPage.data?.nextCursor ?? null);

  const loadMore = useCallback(async () => {
    if (!nextCursor) return;
    setLoadingMore(true);
    setMoreError(null);
    try {
      const page = await fetchPastRides(nextCursor);
      setMorePages((previous) => ({ items: [...(previous?.items ?? []), ...page.items], nextCursor: page.nextCursor }));
    } catch (caught) {
      setMoreError(errorMessage(caught));
    } finally {
      setLoadingMore(false);
    }
  }, [nextCursor]);

  return {
    rides,
    loading: firstPage.loading,
    error: firstPage.error,
    retry: firstPage.retry,
    hasMore: nextCursor !== null,
    loadMore,
    loadingMore,
    moreError,
  };
}
