import { afterEach, describe, expect, it, vi } from 'vitest';

import { en } from './en';
import { fr } from './fr';
import { availableLanguages, language, languageName, locale, setLanguage, subscribeToLanguage, t, tn } from './index';
import { ptBR } from './pt-BR';
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
    expect(availableLanguages()).not.toContain('test');
  });
});

describe('setLanguage', () => {
  it('changes every text at once, and tells the screens', async () => {
    const listener = vi.fn();
    const unsubscribe = subscribeToLanguage(listener);

    await setLanguage('test');

    expect(language()).toBe('test');
    expect(t('auth.loginTitle')).toBe('[Se connecter]');
    expect(t('home.greeting', { name: 'Alice' })).toBe('[Bonjour Alice]');
    expect(listener).toHaveBeenCalledTimes(1);
    unsubscribe();
  });

  it('keeps the format of dates and prices of the language', async () => {
    await setLanguage('test');

    expect(locale()).toBe('fr-FR');
  });

  it('does nothing for the language already shown', async () => {
    const listener = vi.fn();
    const unsubscribe = subscribeToLanguage(listener);

    await setLanguage('fr');

    expect(listener).not.toHaveBeenCalled();
    unsubscribe();
  });
});

describe('the languages offered', () => {
  it('are the five asked by the client, French first', () => {
    expect(availableLanguages()).toEqual(['fr', 'gcr', 'ht', 'pt-BR', 'en']);
  });

  it('are each named in their own language', () => {
    expect(languageName('en')).toBe('English');
    expect(languageName('pt-BR')).toBe('Português (Brasil)');
  });
});

describe.each([
  ['en', en],
  ['pt-BR', ptBR],
] as const)('the translation %s', (_code, texts) => {
  const translated = new Map(leaves(texts));

  it('has exactly the keys of fr.ts', () => {
    expect([...translated.keys()].sort()).toEqual(leaves(fr).map(([key]) => key).sort());
  });

  it('keeps the placeholders of every text, and leaves none empty', () => {
    for (const [key, value] of leaves(fr)) {
      const text = translated.get(key) ?? '';
      expect(text.trim(), key).not.toBe('');
      expect((text.match(PLACEHOLDER) ?? []).sort(), key).toEqual((value.match(PLACEHOLDER) ?? []).sort());
    }
  });
});

describe('a language being translated', () => {
  it('shows a text in its language when it has it', async () => {
    await setLanguage('en');

    expect(t('auth.loginTitle')).toBe('Log in');
    expect(tn('driver.rideCount', 1)).toBe('1 ride');
    expect(tn('driver.rideCount', 2)).toBe('2 rides');
    expect(locale()).toBe('en-GB');
  });

  it('shows French for every text it does not have yet', async () => {
    await setLanguage('gcr');

    expect(language()).toBe('gcr');
    expect(t('auth.loginTitle')).toBe('Se connecter');
    expect(locale()).toBe('fr-FR');
  });
});
