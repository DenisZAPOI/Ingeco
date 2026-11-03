// Dates and times are always shown in Guyana time (UTC−3), whatever the
// phone's time zone (cahier des charges, §3: automated tests on dates).

import { describe, expect, it } from 'vitest';

import { periodBounds } from './earnings';
import { formatDateTime, formatDistance, formatPrice, formatScore, formatTime, guyanaDateTime } from './format';

const NBSP = ' ';

describe('formatTime', () => {
  it('shows the time in Guyana, three hours behind UTC', () => {
    expect(formatTime('2026-10-14T17:30:00Z')).toBe(`14${NBSP}h${NBSP}30`);
  });

  it('keeps the day of Guyana around midnight UTC', () => {
    // 01:00 UTC on the 15th is still 22:00 on the 14th in Cayenne.
    expect(formatDateTime('2026-10-15T01:00:00Z')).toContain('14 octobre');
    expect(formatDateTime('2026-10-15T01:00:00Z')).toContain(`22${NBSP}h${NBSP}00`);
  });
});

describe('guyanaDateTime', () => {
  it('writes a time typed in Guyana with its offset', () => {
    expect(new Date(guyanaDateTime('2026-10-14', '14:30')).toISOString()).toBe('2026-10-14T17:30:00.000Z');
  });
});

describe('periodBounds', () => {
  it('starts the week on Monday', () => {
    // Wednesday 4 November 2026.
    expect(periodBounds('week', '2026-11-04')).toEqual({ from: '2026-11-02', to: '2026-11-04' });
  });

  it('counts a Sunday in the week that started six days before', () => {
    expect(periodBounds('week', '2026-11-08')).toEqual({ from: '2026-11-02', to: '2026-11-08' });
  });

  it('starts the month on the 1st', () => {
    expect(periodBounds('month', '2026-11-04')).toEqual({ from: '2026-11-01', to: '2026-11-04' });
  });
});

describe('numbers', () => {
  it('writes prices, distances and scores the French way', () => {
    expect(formatPrice(1848)).toBe(`18,48${NBSP}€`);
    expect(formatDistance(11.4)).toBe('11,4 km');
    expect(formatScore(4.7)).toBe('4,7 sur 5');
    expect(formatScore(null)).toBe('Pas encore noté');
  });
});
