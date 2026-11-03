// Formats of the charter (docs/charte-graphique.md, part 7), in the current
// language. Dates and times always in Guyana time, whatever the phone's own
// time zone.

import { locale, t } from '../i18n';

export const GUYANA_TIME_ZONE = 'America/Cayenne';
// Guyana has no daylight saving time: the offset never changes.
const GUYANA_UTC_OFFSET = '-03:00';
const CENTS_PER_EURO = 100;
// 'en-CA' writes dates as YYYY-MM-DD, the value of an <input type="date">.
const ISO_DAY = new Intl.DateTimeFormat('en-CA', { timeZone: GUYANA_TIME_ZONE, year: 'numeric', month: '2-digit', day: '2-digit' });

type Formats = {
  price: Intl.NumberFormat;
  decimal: Intl.NumberFormat;
  day: Intl.DateTimeFormat;
  dayWithYear: Intl.DateTimeFormat;
  time: Intl.DateTimeFormat;
  year: Intl.DateTimeFormat;
};

// Building an Intl format is slow: one set per language, built on first use.
const formatsByLocale = new Map<string, Formats>();

function formats(): Formats {
  const tag = locale();
  let found = formatsByLocale.get(tag);
  if (!found) {
    found = {
      price: new Intl.NumberFormat(tag, { style: 'currency', currency: 'EUR' }),
      decimal: new Intl.NumberFormat(tag, { maximumFractionDigits: 1 }),
      day: new Intl.DateTimeFormat(tag, { timeZone: GUYANA_TIME_ZONE, weekday: 'long', day: 'numeric', month: 'long' }),
      dayWithYear: new Intl.DateTimeFormat(tag, {
        timeZone: GUYANA_TIME_ZONE,
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      }),
      time: new Intl.DateTimeFormat(tag, { timeZone: GUYANA_TIME_ZONE, hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }),
      year: new Intl.DateTimeFormat(tag, { timeZone: GUYANA_TIME_ZONE, year: 'numeric' }),
    };
    formatsByLocale.set(tag, found);
  }
  return found;
}

/** 1848 → '18,48 €' */
export function formatPrice(cents: number): string {
  return formats().price.format(cents / CENTS_PER_EURO);
}

/** 4.7 → '4,7 sur 5'; null: never rated. */
export function formatScore(score: number | null): string {
  return score === null ? t('format.notRated') : t('format.score', { score: formats().decimal.format(score) });
}

/** 11.4 → '11,4 km' */
export function formatDistance(km: number): string {
  return t('format.distance', { km: formats().decimal.format(km) });
}

/** '2026-10-14T17:30:00Z' → 'mercredi 14 octobre' (with the year if not this year). */
export function formatDay(iso: string): string {
  const { day, dayWithYear, year } = formats();
  const date = new Date(iso);
  const sameYear = year.format(date) === year.format(new Date());
  return (sameYear ? day : dayWithYear).format(date);
}

/** '2026-10-14T17:30:00Z' → '14 h 30' (non-breaking spaces: never split over two lines). */
export function formatTime(iso: string): string {
  const parts = formats().time.formatToParts(new Date(iso));
  const part = (type: string) => parts.find((entry) => entry.type === type)?.value ?? '';
  return t('format.time', { hour: part('hour'), minute: part('minute') });
}

/** 'mercredi 14 octobre à 14 h 30' */
export function formatDateTime(iso: string): string {
  return t('format.dateTime', { day: formatDay(iso), time: formatTime(iso) });
}

/** Today in Guyana, as 'YYYY-MM-DD'. */
export function guyanaToday(): string {
  return ISO_DAY.format(new Date());
}

/** A day and a time typed in Guyana ('2026-10-14', '14:30') → ISO 8601 with its offset. */
export function guyanaDateTime(day: string, time: string): string {
  return `${day}T${time}:00${GUYANA_UTC_OFFSET}`;
}
