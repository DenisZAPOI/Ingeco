import { afterEach, describe, expect, it, vi } from 'vitest';

import type { StepCode } from '../api/orientation';
import { NO_ANSWER, QUESTIONS, readDraft, saveDraft, stepTarget, toggle } from './orientation';

const needs = QUESTIONS.find((q) => q.field === 'needs')!;
const situation = QUESTIONS.find((q) => q.field === 'situation')!;

describe('toggle', () => {
  it('keeps one answer for a single-choice question', () => {
    const once = toggle(NO_ANSWER, situation, 'sans_emploi', true);
    expect(toggle(once, situation, 'reprise', true).situation).toBe('reprise');
  });

  it('keeps the answers in the order of the questionnaire', () => {
    const answers = toggle(toggle(NO_ANSWER, needs, 'logement', true), needs, 'trajet', true);
    expect(answers.needs).toEqual(['trajet', 'logement']);
  });

  it('ticks « Rien de tout ça » alone, and any other answer clears it', () => {
    const some = toggle(NO_ANSWER, needs, 'trajet', true);
    const nothing = toggle(some, needs, 'aucun', true);
    expect(nothing.needs).toEqual(['aucun']);
    expect(toggle(nothing, needs, 'garde', true).needs).toEqual(['garde']);
  });

  it('unticks an answer', () => {
    const some = toggle(NO_ANSWER, needs, 'trajet', true);
    expect(toggle(some, needs, 'trajet', false).needs).toEqual([]);
  });
});

describe('stepTarget', () => {
  it('leads the offers to the list filtered « débutant accepté »', () => {
    expect(stepTarget('offres')).toBe('/emplois?debutant=1');
  });

  it('leads a need to its category of the directory', () => {
    expect(stepTarget('garde')).toBe('/aide/services?besoin=garde');
    expect(stepTarget('numerique_auto')).toBe('/aide/services?besoin=numerique');
  });

  it('gives every step code a place to go', () => {
    const codes: StepCode[] = [
      'offres', 'formation', 'creer', 'conseiller', 'trajet', 'garde', 'logement',
      'demarches', 'numerique', 'francais', 'equipement', 'francais_auto', 'numerique_auto', 'entretien',
    ];
    for (const code of codes) expect(stepTarget(code)).toMatch(/^\//);
  });
});

describe('draft', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    saveDraft(null);
  });

  it('survives in sessionStorage', () => {
    const store = new Map<string, string>();
    vi.stubGlobal('sessionStorage', {
      getItem: (key: string) => store.get(key) ?? null,
      setItem: (key: string, value: string) => store.set(key, value),
      removeItem: (key: string) => store.delete(key),
    });
    saveDraft({ answers: { ...NO_ANSWER, project: 'formation' }, finished: true });
    expect(readDraft()).toEqual({ answers: { ...NO_ANSWER, project: 'formation' }, finished: true });
  });

  it('stays in memory when the storage is refused', () => {
    const refused = () => {
      throw new Error('blocked');
    };
    vi.stubGlobal('sessionStorage', { getItem: refused, setItem: refused, removeItem: refused });
    saveDraft({ answers: NO_ANSWER, finished: false });
    expect(readDraft()).toEqual({ answers: NO_ANSWER, finished: false });
  });
});
