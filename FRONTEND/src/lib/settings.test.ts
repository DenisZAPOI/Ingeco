import { describe, expect, it } from 'vitest';

import { dayForms, eurosField, examplePriceCents, parseEuros, timeField, weekBody } from './settings';

describe('parseEuros', () => {
  it('reads euros written with a comma or a point', () => {
    expect(parseEuros('8,50')).toBe(850);
    expect(parseEuros('8.5')).toBe(850);
    expect(parseEuros(' 8 ')).toBe(800);
    expect(parseEuros('0,80')).toBe(80);
  });

  it('refuses what is not an amount', () => {
    expect(parseEuros('')).toBeNull();
    expect(parseEuros('huit')).toBeNull();
    expect(parseEuros('8,505')).toBeNull();
    expect(parseEuros('-8')).toBeNull();
  });
});

describe('eurosField', () => {
  it('writes cents as euros with two decimals', () => {
    expect(eurosField(800)).toBe('8,00');
    expect(eurosField(85)).toBe('0,85');
  });
});

describe('examplePriceCents', () => {
  it('is the pickup fare plus the price per km', () => {
    expect(examplePriceCents(800, 80, 10)).toBe(1600);
  });
});

describe('service hours', () => {
  it('shows the times of the API as hours and minutes, a closed day as closed', () => {
    const forms = dayForms([
      { weekday: 1, opensAt: '06:00:00', closesAt: '23:59:59' },
      { weekday: 7, opensAt: null, closesAt: null },
    ]);

    expect(forms).toEqual([
      { weekday: 1, closed: false, opensAt: '06:00', closesAt: '23:59' },
      { weekday: 7, closed: true, opensAt: '', closesAt: '' },
    ]);
    expect(timeField(null)).toBe('');
  });

  it('sends a closed day, and an empty time, as null', () => {
    const body = weekBody([
      { weekday: 1, closed: false, opensAt: '06:00', closesAt: '' },
      { weekday: 7, closed: true, opensAt: '08:00', closesAt: '12:00' },
    ]);

    expect(body.days).toEqual([
      { weekday: 1, opensAt: '06:00', closesAt: null },
      { weekday: 7, opensAt: null, closesAt: null },
    ]);
  });
});
