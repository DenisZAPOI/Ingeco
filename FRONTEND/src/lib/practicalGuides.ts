import type { HelpCategory } from '../api/helpServices';
import type { PracticalGuide } from '../api/practicalGuides';
import { language, t } from '../i18n';
import { HELP_CATEGORIES } from './helpServices';

// Practical guides "Comment faire ?" (module M5): loaded once (GET
// /practical-guides), kept on the phone, filtered by need.

export function guidesOfCategory(guides: readonly PracticalGuide[], category: HelpCategory): PracticalGuide[] {
  return guides.filter((guide) => guide.category === category);
}

/** What the phone reads aloud: the title, the introduction, each step with its
 *  number, then what to bring. One text, so that "Arrêter" stops it all. */
export function guideSpeechText(guide: PracticalGuide): string {
  const parts = [guide.title, guide.intro];
  guide.steps.forEach((step, index) => parts.push(t('guides.stepSpoken', { number: index + 1, step })));
  if (guide.toBring.length > 0) {
    parts.push(t('guides.bringSpoken', { list: guide.toBring.join(', ') }));
  }
  return parts.join('\n');
}

/** Whether a voice of the phone speaks this language ("fr" matches "fr-FR"). */
export function hasVoiceFor(voices: readonly { lang: string }[], lang: string): boolean {
  return voices.some((voice) => sameLanguage(voice.lang, lang));
}

/** "pt-BR", "pt_BR" and "pt" are the same language for a voice. */
export function sameLanguage(voiceLang: string, lang: string): boolean {
  const base = (code: string) => code.toLowerCase().replace('_', '-').split('-')[0];
  return base(voiceLang) === base(lang);
}

// The last list received, shown at once on the next visit while the API
// confirms it. Kept with its language (ADR 018).

const STORAGE_KEY = 'practical-guides';

export function readStoredGuides(): PracticalGuide[] | null {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? 'null');
    if (typeof parsed !== 'object' || parsed === null) return null;
    const { language: storedIn, guides } = parsed as { language: unknown; guides: unknown };
    if (storedIn === language() && Array.isArray(guides) && guides.every(isGuide)) {
      return guides;
    }
  } catch {
    // Storage blocked or corrupted: no head start.
  }
  return null;
}

export function storeGuides(guides: PracticalGuide[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ language: language(), guides }));
  } catch {
    // Storage blocked: fetched again next time.
  }
}

/** Enough to show a guide: one kept by an older version is dropped. */
function isGuide(value: unknown): value is PracticalGuide {
  if (typeof value !== 'object' || value === null) return false;
  const { id, title, category, steps, toBring } = value as Record<string, unknown>;
  return (
    typeof id === 'number' &&
    typeof title === 'string' &&
    HELP_CATEGORIES.some((known) => known === category) &&
    Array.isArray(steps) &&
    Array.isArray(toBring)
  );
}

/** The guide handed over by the list (router state), if it is this one. */
export function guideFromState(state: unknown, id: number): PracticalGuide | null {
  if (typeof state !== 'object' || state === null || !('guide' in state)) return null;
  const { guide } = state as { guide: unknown };
  return isGuide(guide) && guide.id === id ? guide : null;
}
