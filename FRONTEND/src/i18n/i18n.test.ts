import { afterEach, describe, expect, it, vi } from 'vitest';

import { fr } from './fr';
import { availableLanguages, language, locale, setLanguage, subscribeToLanguage, t, tn } from './index';
import { pseudoLanguage } from './pseudo';

/** Every 'a.b.c' key of a texts object, with its value. */
function leaves(texts: object, prefix = ''): [string, string][] {
  return Object.entries(texts).flatMap(([key, value]) =>
    typeof value === 'string' ? [[`${prefix}${key}`, value] as [string, string]] : leaves(value, `${prefix}${key}.`),
  );
}

const PLACEHOLDER = /\{\w+\}/g;

afterEach(() => setLanguage('fr'));

describe('t', () => {
  it('returns the French text of a key', () => {
    expect(t('auth.loginTitle')).toBe('Se connecter');
  });

  it('fills the placeholders', () => {
    expect(t('home.greeting', { name: 'Alice' })).toBe('Bonjour Alice');
    expect(t('booking.step', { step: 2, total: 4 })).toBe('Étape 2 sur 4');
  });
});

describe('tn', () => {
  it('uses the singular for 0 and 1 in French', () => {
    expect(tn('driver.rideCount', 0)).toBe('0 course');
    expect(tn('driver.rideCount', 1)).toBe('1 course');
  });

  it('uses the plural from 2', () => {
    expect(tn('driver.rideCount', 3)).toBe('3 courses');
    expect(tn('rating.stars', 5)).toBe('5 étoiles sur 5');
  });
});

describe('fr.ts', () => {
  const all = leaves(fr);

  it('has no empty text', () => {
    expect(all.filter(([, value]) => value.trim() === '')).toEqual([]);
  });

  it('gives every plural both forms', () => {
    const keys = new Set(all.map(([key]) => key));
    const orphans = [...keys]
      .filter((key) => /_(one|other)$/.test(key))
      .filter((key) => !keys.has(key.replace(/_(one|other)$/, '_one')) || !keys.has(key.replace(/_(one|other)$/, '_other')));
    expect(orphans).toEqual([]);
  });
});

describe('the test language', () => {
  it('has every key of fr.ts, between brackets, with the same placeholders', () => {
    const pseudo = new Map(leaves(pseudoLanguage(fr)));
    for (const [key, value] of leaves(fr)) {
      const translated = pseudo.get(key);
      expect(translated, key).toBe(`[${value}]`);
      expect(translated?.match(PLACEHOLDER) ?? [], key).toEqual(value.match(PLACEHOLDER) ?? []);
    }
  });

  it('is not offered to the user', () => {
    expect(availableLanguages()).toEqual(['fr']);
  });
});

describe('setLanguage', () => {
  it('changes every text at once, and tells the screens', () => {
    const listener = vi.fn();
    const unsubscribe = subscribeToLanguage(listener);

    setLanguage('test');

    expect(language()).toBe('test');
    expect(t('auth.loginTitle')).toBe('[Se connecter]');
    expect(t('home.greeting', { name: 'Alice' })).toBe('[Bonjour Alice]');
    expect(listener).toHaveBeenCalledTimes(1);
    unsubscribe();
  });

  it('keeps the format of dates and prices of the language', () => {
    setLanguage('test');

    expect(locale()).toBe('fr-FR');
  });

  it('does nothing for the language already shown', () => {
    const listener = vi.fn();
    const unsubscribe = subscribeToLanguage(listener);

    setLanguage('fr');

    expect(listener).not.toHaveBeenCalled();
    unsubscribe();
  });
});
