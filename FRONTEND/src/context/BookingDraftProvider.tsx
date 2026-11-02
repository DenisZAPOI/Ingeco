import { useCallback, useMemo, useState, type ReactNode } from 'react';

import { readBookingDraft, saveBookingDraft, type BookingDraft } from '../lib/bookingDraft';
import { BookingDraftContext, type BookingDraftState } from './bookingDraftContext';

/** The booking being typed, shared by its steps (one page each). */
export function BookingDraftProvider({ children }: { children: ReactNode }) {
  const [draft, setDraft] = useState<BookingDraft>(readBookingDraft);

  const change = useCallback((next: (current: BookingDraft) => BookingDraft) => {
    setDraft((current) => {
      const updated = next(current);
      saveBookingDraft(updated);
      return updated;
    });
  }, []);

  const update = useCallback<BookingDraftState['update']>(
    (changes) => change((current) => ({ ...current, ...changes, requestId: null })),
    [change],
  );
  const setRequestId = useCallback((requestId: string) => change((current) => ({ ...current, requestId })), [change]);
  const value = useMemo(() => ({ draft, update, setRequestId }), [draft, update, setRequestId]);
  return <BookingDraftContext.Provider value={value}>{children}</BookingDraftContext.Provider>;
}
