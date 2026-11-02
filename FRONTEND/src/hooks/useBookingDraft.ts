import { useContext } from 'react';

import { BookingDraftContext, type BookingDraftState } from '../context/bookingDraftContext';

export function useBookingDraft(): BookingDraftState {
  const state = useContext(BookingDraftContext);
  if (state === null) {
    throw new Error('useBookingDraft must be used inside <BookingDraftProvider>.');
  }
  return state;
}
