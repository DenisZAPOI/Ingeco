/**
 * Texts of the interface (cahier des charges, §6: every text in translation
 * files, the language can change at any time). Decision: docs/adr/013.
 *
 *   t('auth.login.title')                    → 'Se connecter'
 *   t('home.greeting', { name: 'Alice' })    → 'Bonjour Alice'
 *   tn('rides.seats', 3)                     → '3 places'  (keys seats_one / seats_other)
 *
 * TypeScript refuses an unknown key or a missing value. Never keep a
 * translated text in a module-level constant: it would not follow a change of
 * language. Call t() where the text is shown, or in a function.
 */

import { fr } from './fr';
import { gcr } from './gcr';
import { ht } from './ht';
import { pseudoLanguage } from './pseudo';

type Widen<T> = { readonly [K in keyof T]: T[K] extends string ? string : Widen<T[K]> };
/** What every language must provide: the keys of fr.ts, with its own wording. */
export type Texts = Widen<typeof fr>;

type Leaves<T, Prefix extends string = ''> = {
  [K in keyof T & string]: T[K] extends string ? `${Prefix}${K}` : Leaves<T[K], `${Prefix}${K}.`>;
}[keyof T & string];
export type TextKey = Leaves<typeof fr>;

type Partially<T> = { readonly [K in keyof T]?: T[K] extends string ? string : Partially<T[K]> };
/** A language still being translated: every text it lacks is shown in French. */
export type PartialTexts = Partially<Texts>;

type At<T, K extends string> = K extends `${infer Head}.${infer Rest}`
  ? Head extends keyof T
    ? At<T[Head], Rest>
    : never
  : K extends keyof T
    ? T[K]
    : never;

type Placeholders<S> = S extends `${string}{${infer Name}}${infer Rest}` ? Name | Placeholders<Rest> : never;
type Values<Names extends string> = Readonly<Record<Names, string | number>>;
type ValuesArg<Names extends string> = [Names] extends [never] ? [] : [values: Values<Names>];

type PluralBase<K> = K extends `${infer Base}_one` ? (`${Base}_other` extends TextKey ? Base : never) : never;
/** A text with a singular and a plural form: `${key}_one` and `${key}_other`. */
export type PluralKey = PluralBase<TextKey>;
type PluralNames<B extends PluralKey> = Exclude<
  Placeholders<At<typeof fr, `${B}_one`>> | Placeholders<At<typeof fr, `${B}_other`>>,
  'count'
>;

// The five languages asked by the client (interview of 03/11/2026, docs/decisions.md).
export type Language = 'fr' | 'en' | 'pt-BR' | 'gcr' | 'ht' | 'test';

type LanguageInfo = {
  /** null until downloaded: see `load`. */
  texts: PartialTexts | null;
  /** A complete translation is a separate file, downloaded only by whoever
   *  chooses it: French speakers do not pay its weight on a slow network. */
  load?: () => Promise<PartialTexts>;
  /** For dates, prices and plurals (Intl). */
  locale: string;
  /** The name of the language written in that language: read by whoever speaks it. */
  name: string;
};

const DEFAULT_LANGUAGE: Language = 'fr';
const STORAGE_KEY = 'langue';

// The two creoles have no text yet (to be written or proofread by speakers):
// they show French. Their dates and prices follow the French format, which
// Intl knows; it does not know these languages.
const LANGUAGES: Partial<Record<Language, LanguageInfo>> = {
  fr: { texts: fr, locale: 'fr-FR', name: 'Français' },
  gcr: { texts: gcr, locale: 'fr-FR', name: 'Kriyòl gwiyanè' },
  ht: { texts: ht, locale: 'fr-FR', name: 'Kreyòl ayisyen' },
  'pt-BR': {
    texts: null,
    load: () => import('./pt-BR').then((module) => module.ptBR),
    locale: 'pt-BR',
    name: 'Português (Brasil)',
  },
  en: { texts: null, load: () => import('./en').then((module) => module.en), locale: 'en-GB', name: 'English' },
};
// Development only: every text between brackets, to spot one left in the code
// (localStorage.langue = 'test', then reload). Absent from the built app.
if (import.meta.env.DEV) {
  LANGUAGES.test = { texts: pseudoLanguage(fr), locale: 'fr-FR', name: 'Test' };
}

let current: Language = storedLanguage() ?? DEFAULT_LANGUAGE;
const listeners = new Set<() => void>();
applyToDocument();

export function language(): Language {
  return current;
}

/** The languages the user can choose: a selector is only worth showing from two. */
export function availableLanguages(): Language[] {
  return (Object.keys(LANGUAGES) as Language[]).filter((code) => code !== 'test');
}

/** The name of a language, written in that language (for the selector). */
export function languageName(code: Language): string {
  return info(code).name;
}

/** Tag for Intl (dates, numbers, plurals) in the current language. */
export function locale(): string {
  return info(current).locale;
}

/** Changes the language of every screen, and remembers it on this phone.
 *  Rejects if its texts cannot be downloaded (no network): the language shown
 *  stays the same. */
export async function setLanguage(code: Language): Promise<void> {
  if (!LANGUAGES[code] || code === current) return;
  await loadTexts(code);
  current = code;
  try {
    localStorage.setItem(STORAGE_KEY, code);
  } catch {
    // Storage blocked: the choice lasts until the page is closed.
  }
  applyToDocument();
  listeners.forEach((listener) => listener());
}

/** At startup, before the first screen: downloads the texts of the language
 *  chosen on an earlier visit. Without network, the app starts in French. */
export async function loadStoredLanguage(): Promise<void> {
  try {
    await loadTexts(current);
  } catch {
    current = DEFAULT_LANGUAGE;
    applyToDocument();
  }
}

async function loadTexts(code: Language): Promise<void> {
  const entry = LANGUAGES[code];
  if (entry && !entry.texts && entry.load) {
    entry.texts = await entry.load();
  }
}

export function subscribeToLanguage(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function t<K extends TextKey>(key: K, ...[values]: ValuesArg<Placeholders<At<typeof fr, K>>>): string {
  return fill(lookup(key), values);
}

/** The singular or plural form, chosen by the rules of the language; {count} is filled in. */
export function tn<B extends PluralKey>(key: B, count: number, ...[values]: ValuesArg<PluralNames<B>>): string {
  const form = new Intl.PluralRules(locale()).select(count) === 'one' ? 'one' : 'other';
  return fill(lookup(`${key}_${form}`), { ...values, count });
}

function lookup(key: string): string {
  return find(info(current).texts, key) ?? find(fr, key) ?? key;
}

function find(texts: unknown, key: string): string | null {
  let node: unknown = texts;
  for (const part of key.split('.')) {
    if (typeof node !== 'object' || node === null) return null;
    node = (node as Record<string, unknown>)[part];
  }
  return typeof node === 'string' ? node : null;
}

function fill(text: string, values: Values<string> | undefined): string {
  if (!values) return text;
  return text.replace(/\{(\w+)\}/g, (match, name: string) => (name in values ? String(values[name]) : match));
}

function info(code: Language): LanguageInfo {
  return LANGUAGES[code] ?? (LANGUAGES[DEFAULT_LANGUAGE] as LanguageInfo);
}

function storedLanguage(): Language | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored && stored in LANGUAGES ? (stored as Language) : null;
  } catch {
    return null;
  }
}

function applyToDocument(): void {
  if (typeof document !== 'undefined') {
    document.documentElement.lang = current === 'test' ? DEFAULT_LANGUAGE : current;
  }
}
