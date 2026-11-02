import { createContext } from 'react';

import type { BookingDraft } from '../lib/bookingDraft';

export type BookingDraftState = {
  draft: BookingDraft;
  /** Any change of the trip makes it a new booking: its requestId is dropped. */
  update: (changes: Partial<Omit<BookingDraft, 'requestId'>>) => void;
  /** Gives the draft its requestId, once, at the confirmation. */
  setRequestId: (requestId: string) => void;
};

export const BookingDraftContext = createContext<BookingDraftState | null>(null);
