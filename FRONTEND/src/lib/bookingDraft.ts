import type { Purpose, Stop } from '../api/rides';

// The booking being typed, step by step. Kept in sessionStorage: it survives
// a reload or the phone's Back button, and disappears with the tab (a shared
// phone does not keep someone else's addresses).

const STORAGE_KEY = 'booking-draft';

export type When = 'now' | 'later';

export type BookingDraft = {
  pickup: Stop | null;
  dropoff: Stop | null;
  purpose: Purpose | null;
  when: When;
  /** 'YYYY-MM-DD' and 'HH:MM', in Guyana time, when `when` is 'later'. */
  day: string;
  time: string;
  /** Created at the confirmation, reused by every retry of that booking. */
  requestId: string | null;
};

const EMPTY_DRAFT: BookingDraft = {
  pickup: null,
  dropoff: null,
  purpose: null,
  when: 'now',
  day: '',
  time: '',
  requestId: null,
};

export function readBookingDraft(): BookingDraft {
  try {
    const parsed: unknown = JSON.parse(sessionStorage.getItem(STORAGE_KEY) ?? 'null');
    if (typeof parsed === 'object' && parsed !== null) {
      return { ...EMPTY_DRAFT, ...(parsed as Partial<BookingDraft>) };
    }
  } catch {
    // Storage blocked or corrupted: start again.
  }
  return EMPTY_DRAFT;
}

export function saveBookingDraft(draft: BookingDraft | null): void {
  try {
    if (draft) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
    } else {
      sessionStorage.removeItem(STORAGE_KEY);
    }
  } catch {
    // Storage blocked: the draft lives in memory only.
  }
}
