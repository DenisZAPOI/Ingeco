// French formats of the charter (docs/charte-graphique.md, part 7). Dates and
// times always in Guyana time, whatever the phone's own time zone.

export const GUYANA_TIME_ZONE = 'America/Cayenne';
// Guyana has no daylight saving time: the offset never changes.
const GUYANA_UTC_OFFSET = '-03:00';
const CENTS_PER_EURO = 100;

const PRICE = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' });
const DISTANCE = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 1 });
const DAY = new Intl.DateTimeFormat('fr-FR', { timeZone: GUYANA_TIME_ZONE, weekday: 'long', day: 'numeric', month: 'long' });
const DAY_WITH_YEAR = new Intl.DateTimeFormat('fr-FR', {
  timeZone: GUYANA_TIME_ZONE,
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric',
});
const TIME = new Intl.DateTimeFormat('fr-FR', { timeZone: GUYANA_TIME_ZONE, hour: '2-digit', minute: '2-digit', hourCycle: 'h23' });
// 'en-CA' writes dates as YYYY-MM-DD, the value of an <input type="date">.
const ISO_DAY = new Intl.DateTimeFormat('en-CA', { timeZone: GUYANA_TIME_ZONE, year: 'numeric', month: '2-digit', day: '2-digit' });
const YEAR = new Intl.DateTimeFormat('fr-FR', { timeZone: GUYANA_TIME_ZONE, year: 'numeric' });

/** 1848 → '18,48 €' */
export function formatPrice(cents: number): string {
  return PRICE.format(cents / CENTS_PER_EURO);
}

/** 11.4 → '11,4 km' */
export function formatDistance(km: number): string {
  return `${DISTANCE.format(km)} km`;
}

/** '2026-10-14T17:30:00Z' → 'mercredi 14 octobre' (with the year if not this year). */
export function formatDay(iso: string): string {
  const date = new Date(iso);
  const sameYear = YEAR.format(date) === YEAR.format(new Date());
  return (sameYear ? DAY : DAY_WITH_YEAR).format(date);
}

/** '2026-10-14T17:30:00Z' → '14 h 30' */
export function formatTime(iso: string): string {
  const parts = TIME.formatToParts(new Date(iso));
  const part = (type: string) => parts.find((entry) => entry.type === type)?.value ?? '';
  return `${part('hour')} h ${part('minute')}`;
}

/** 'mercredi 14 octobre à 14 h 30' */
export function formatDateTime(iso: string): string {
  return `${formatDay(iso)} à ${formatTime(iso)}`;
}

/** Today in Guyana, as 'YYYY-MM-DD'. */
export function guyanaToday(): string {
  return ISO_DAY.format(new Date());
}

/** A day and a time typed in Guyana ('2026-10-14', '14:30') → ISO 8601 with its offset. */
export function guyanaDateTime(day: string, time: string): string {
  return `${day}T${time}:00${GUYANA_UTC_OFFSET}`;
}
