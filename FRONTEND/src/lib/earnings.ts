import { t, tn } from '../i18n';
import { formatDay, guyanaDateTime, guyanaToday } from './format';

// The driver's periods (UC28), counted like a driver does: the week starts on
// Monday, the month on the 1st. Days in Guyana time, as the API expects.

export type EarningsPeriod = 'today' | 'week' | 'month';

export function periodLabel(period: EarningsPeriod): string {
  return t(`driver.${period}`);
}

const MS_PER_DAY = 24 * 60 * 60 * 1000;
const MONDAY = 1;
const DAYS_PER_WEEK = 7;
// Noon: a 'YYYY-MM-DD' read at midnight UTC would be the day before in Guyana.
const MIDDAY = '12:00';

/** First and last day of the period containing `today` ('YYYY-MM-DD'), both included. */
export function periodBounds(period: EarningsPeriod, today: string = guyanaToday()): { from: string; to: string } {
  if (period === 'today') return { from: today, to: today };
  if (period === 'month') return { from: `${today.slice(0, 7)}-01`, to: today };
  // Calendar arithmetic on the day itself, in UTC: no time zone can shift it.
  const date = new Date(`${today}T00:00:00Z`);
  // getUTCDay: 0 is Sunday, 1 Monday… Monday → 0 days back, Sunday → 6.
  const daysSinceMonday = (date.getUTCDay() + DAYS_PER_WEEK - MONDAY) % DAYS_PER_WEEK;
  const monday = new Date(date.getTime() - daysSinceMonday * MS_PER_DAY);
  return { from: monday.toISOString().slice(0, 10), to: today };
}

/** '2026-11-02' → 'lundi 2 novembre' */
export function formatEarningsDay(day: string): string {
  return formatDay(guyanaDateTime(day, MIDDAY));
}

/** 1 → '1 course', 3 → '3 courses' */
export function formatRideCount(count: number): string {
  return tn('driver.rideCount', count);
}
