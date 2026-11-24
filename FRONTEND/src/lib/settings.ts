import type { DayHours, WeekBody } from '../api/settings';
import type { TextKey } from '../i18n';

// Pure logic of the administrator's settings screen: no React.

const CENTS_PER_EURO = 100;
// "8", "8,5", "8,50" or "8.50": euros with at most two decimals.
const EUROS_PATTERN = /^\d+(?:[.,]\d{1,2})?$/;
// "06:00:00" from the API, "06:00" in a time field.
const HOURS_AND_MINUTES_LENGTH = 5;

/** The example shown under the tariff: what a trip of this length will cost. */
export const TARIFF_EXAMPLE_KM = 10;

/** Name of each day, Monday (1) to Sunday (7), as in the API. */
export const DAY_NAME_KEYS = {
  1: 'settings.monday',
  2: 'settings.tuesday',
  3: 'settings.wednesday',
  4: 'settings.thursday',
  5: 'settings.friday',
  6: 'settings.saturday',
  7: 'settings.sunday',
} as const satisfies Record<number, TextKey>;

export type Weekday = keyof typeof DAY_NAME_KEYS;

/** One day as the form holds it: text fields, and a "Closed" box. */
export type DayForm = {
  weekday: Weekday;
  closed: boolean;
  opensAt: string;
  closesAt: string;
};

/** '06:00:00' → '06:00'; null → ''. */
export function timeField(apiTime: string | null): string {
  if (apiTime === null) return '';
  return apiTime.slice(0, HOURS_AND_MINUTES_LENGTH);
}

export function dayForms(days: DayHours[]): DayForm[] {
  return days.map((day) => ({
    weekday: day.weekday as Weekday,
    closed: day.opensAt === null,
    opensAt: timeField(day.opensAt),
    closesAt: timeField(day.closesAt),
  }));
}

/** The body of PUT /admin/service-hours. An empty time is sent as null: the API explains what is missing. */
export function weekBody(days: DayForm[]): WeekBody {
  return {
    days: days.map((day) => {
      if (day.closed) {
        return { weekday: day.weekday, opensAt: null, closesAt: null };
      }
      return { weekday: day.weekday, opensAt: day.opensAt || null, closesAt: day.closesAt || null };
    }),
  };
}

/** '8,50' or '8.5' → 850; null if the text is not an amount in euros. */
export function parseEuros(text: string): number | null {
  const trimmed = text.trim();
  if (!EUROS_PATTERN.test(trimmed)) return null;
  const euros = Number(trimmed.replace(',', '.'));
  return Math.round(euros * CENTS_PER_EURO);
}

/** 850 → '8,50', to fill a field. */
export function eurosField(cents: number): string {
  const euros = Math.floor(cents / CENTS_PER_EURO);
  const rest = String(cents % CENTS_PER_EURO).padStart(2, '0');
  return `${euros},${rest}`;
}

/** Price of a trip of `km` kilometres with this tariff, in cents (as the API rounds it). */
export function examplePriceCents(baseFareCents: number, perKmCents: number, km: number): number {
  return Math.round(baseFareCents + perKmCents * km);
}
