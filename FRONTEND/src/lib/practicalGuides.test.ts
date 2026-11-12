// Practical guides: filtered by need, read aloud in one text, and the
// "Écouter" button only when the phone has a voice for the guide's language.

import { afterEach, describe, expect, it, vi } from 'vitest';

import type { PracticalGuide } from '../api/practicalGuides';
import { setLanguage } from '../i18n';
import {
  guideFromState,
  guideSpeechText,
  guidesOfCategory,
  hasVoiceFor,
  readStoredGuides,
  sameLanguage,
  storeGuides,
} from './practicalGuides';

function guide(changes: Partial<PracticalGuide>): PracticalGuide {
  return {
    id: 7,
    category: 'paperwork',
    title: "S'inscrire à France Travail",
    intro: 'Un conseiller, des offres, des formations.',
    steps: ['Inscrivez-vous en ligne.', 'Prenez le rendez-vous.'],
    toBring: ["Une pièce d'identité", 'Un CV'],
    source: { name: 'France Travail', url: 'https://www.francetravail.fr/' },
    updatedOn: '2026-11-11',
    language: 'fr',
    ...changes,
  };
}

const PAPERWORK = guide({});
const FOOD = guide({ id: 5, category: 'food', toBring: [], source: null });

describe('guidesOfCategory', () => {
  it('keeps the guides of one need', () => {
    expect(guidesOfCategory([PAPERWORK, FOOD], 'food')).toEqual([FOOD]);
    expect(guidesOfCategory([PAPERWORK, FOOD], 'housing')).toEqual([]);
  });
});

describe('guideSpeechText', () => {
  it('reads the title, the introduction, each numbered step, then what to bring', () => {
    expect(guideSpeechText(PAPERWORK).split('\n')).toEqual([
      "S'inscrire à France Travail",
      'Un conseiller, des offres, des formations.',
      'Étape 1 : Inscrivez-vous en ligne.',
      'Étape 2 : Prenez le rendez-vous.',
      "À apporter : Une pièce d'identité, Un CV.",
    ]);
  });

  it('says nothing to bring when there is nothing', () => {
    expect(guideSpeechText(FOOD)).not.toContain('apporter');
  });
});

describe('voices', () => {
  it('match a language whatever the region or the separator', () => {
    expect(sameLanguage('fr-FR', 'fr')).toBe(true);
    expect(sameLanguage('pt_BR', 'pt-BR')).toBe(true);
    expect(sameLanguage('en-GB', 'fr')).toBe(false);
  });

  it('offer "Écouter" only when the phone has a voice for the guide', () => {
    const voices = [{ lang: 'fr-FR' }, { lang: 'en-US' }];

    expect(hasVoiceFor(voices, 'fr')).toBe(true);
    expect(hasVoiceFor(voices, 'pt-BR')).toBe(false);
    expect(hasVoiceFor([], 'fr')).toBe(false);
  });
});

describe('a guide', () => {
  afterEach(async () => {
    await setLanguage('fr');
    vi.unstubAllGlobals();
  });

  it('is handed over by the list only if it is the one asked for', () => {
    expect(guideFromState({ guide: PAPERWORK }, 7)).toEqual(PAPERWORK);
    expect(guideFromState({ guide: PAPERWORK }, 5)).toBeNull();
    expect(guideFromState({ guide: { id: 7 } }, 7)).toBeNull();
  });

  it('kept on the phone is shown again only in the language it was received in', async () => {
    const stored = new Map<string, string>();
    vi.stubGlobal('localStorage', {
      getItem: (key: string) => stored.get(key) ?? null,
      setItem: (key: string, value: string) => stored.set(key, value),
    });

    storeGuides([PAPERWORK, FOOD]);
    expect(readStoredGuides()?.map((found) => found.id)).toEqual([7, 5]);

    await setLanguage('en');
    expect(readStoredGuides()).toBeNull();
  });
});
