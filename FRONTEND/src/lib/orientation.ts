import type { HelpCategory } from '../api/helpServices';
import type { Answers, StepCode } from '../api/orientation';
import { filtersToParams as helpParams } from './helpServices';
import { NO_FILTER, filtersToParams as jobParams } from './jobs';
import { BOOKING_PATHS, CALLBACK_PATH, HELP_SERVICES_PATH, JOBS_PATH, TRAININGS_PATH, guidePath } from './paths';

// The orientation questionnaire (module M1, cahier des charges §7.1): seven
// questions, as in the validated mockup. Codes only here: the texts are in
// i18n (orientation.questions.<field>), shown with t().

/** The fields of the answers that hold one question each (the free text goes with "experiences"). */
export type QuestionField = Exclude<keyof Answers, 'experienceText'>;
type Choices<Field extends QuestionField> = NonNullable<Answers[Field]> extends readonly (infer Code)[] ? Code : NonNullable<Answers[Field]>;

/** Every answer code of the questionnaire (keys of orientation.answers in i18n). */
export type AnswerCode = { [Field in QuestionField]: Choices<Field> }[QuestionField];

export type Question = {
  field: QuestionField;
  multiple: boolean;
  choices: readonly AnswerCode[];
  /** "Nothing of all that": ticked alone. */
  alone?: AnswerCode;
};

function question<Field extends QuestionField>(
  field: Field,
  multiple: boolean,
  choices: readonly Choices<Field>[],
  alone?: Choices<Field>,
): Question {
  // Choices<Field> is one part of AnswerCode, which TypeScript cannot see through the generic.
  return { field, multiple, choices: choices as readonly AnswerCode[], alone: alone as AnswerCode | undefined };
}

export const QUESTIONS: readonly Question[] = [
  question('situation', false, ['sans_emploi', 'petits_boulots', 'en_emploi', 'en_formation', 'reprise']),
  question('project', false, ['travail_vite', 'formation', 'creer', 'ne_sait_pas']),
  question(
    'experiences',
    true,
    ['agriculture', 'peche', 'artisanat', 'garde_enfants', 'aide_personne', 'menage', 'batiment', 'cuisine', 'vente', 'benevolat', 'aucune'],
    'aucune',
  ),
  question('availability', true, ['matin', 'apres_midi', 'soir', 'nuit', 'week_end']),
  question(
    'needs',
    true,
    ['trajet', 'vehicule_adapte', 'garde', 'logement', 'demarches', 'numerique', 'francais', 'equipement', 'aucun'],
    'aucun',
  ),
  // Never the languages spoken: they hint at an origin (cahier des charges §12, audit RGPD R6).
  question('french', false, ['oui', 'un_peu', 'non']),
  question('digitalEquipment', true, ['smartphone', 'ordinateur', 'internet_maison', 'email', 'rien'], 'rien'),
];

/** Same limit as the API (orientation_rules.EXPERIENCE_TEXT_MAX_LENGTH). */
export const EXPERIENCE_TEXT_MAX_LENGTH = 500;

export const NO_ANSWER: Answers = {
  situation: null,
  project: null,
  experiences: [],
  experienceText: null,
  availability: [],
  needs: [],
  french: null,
  digitalEquipment: [],
};

/** The codes chosen for a question, single or multiple. */
export function chosen(answers: Answers, field: QuestionField): AnswerCode[] {
  const value: AnswerCode | readonly AnswerCode[] | null | undefined = answers[field];
  if (Array.isArray(value)) return [...value];
  return typeof value === 'string' ? [value] : [];
}

/** Ticks or unticks one answer. "Nothing of all that" clears the others, and any other clears it. */
export function toggle(answers: Answers, q: Question, code: AnswerCode, on: boolean): Answers {
  if (!q.multiple) return { ...answers, [q.field]: on ? code : null };
  const current = chosen(answers, q.field);
  let next: AnswerCode[];
  if (!on) next = current.filter((value) => value !== code);
  else if (code === q.alone) next = [code];
  else next = [...current.filter((value) => value !== q.alone && value !== code), code];
  // In the order of the questionnaire, as the API sends them back.
  return { ...answers, [q.field]: q.choices.filter((value) => next.includes(value)) };
}

/** Where the button of a step leads (lists the person filters herself, never a chosen offer). */
export function stepTarget(code: StepCode): string {
  switch (code) {
    case 'offres':
      return `${JOBS_PATH}?${new URLSearchParams(jobParams({ ...NO_FILTER, beginnerWelcome: true }))}`;
    case 'formation':
    case 'francais':
    case 'francais_auto':
      return TRAININGS_PATH;
    case 'creer':
    case 'demarches':
      return helpCategory('paperwork');
    case 'garde':
      return helpCategory('childcare');
    case 'logement':
      return helpCategory('housing');
    case 'equipement':
      return helpCategory('equipment');
    case 'numerique':
    case 'numerique_auto':
      return helpCategory('digital');
    case 'trajet':
      return BOOKING_PATHS.pickup;
    case 'conseiller':
      return CALLBACK_PATH;
    case 'entretien':
      return guidePath(INTERVIEW_GUIDE_ID);
  }
}

/** « Trouver une tenue pour un entretien » (migration 016): no guide on the interview itself yet. */
const INTERVIEW_GUIDE_ID = 8;

function helpCategory(category: HelpCategory): string {
  return `${HELP_SERVICES_PATH}?${new URLSearchParams(helpParams({ category, communeId: null }))}`;
}

// --- The answers being typed, kept in sessionStorage -----------------------------
// They survive the login or the registration of "Garder mon plan", and
// disappear with the tab: a shared phone does not keep someone else's answers.
// Not kept on the API without an account (cahier des charges §2).

const STORAGE_KEY = 'orientation-answers';

type Draft = { answers: Answers; finished: boolean };

// When the storage is refused (private window, blocked site data): the
// answers last as long as the page.
let inMemory: Draft | null = null;

export function readDraft(): Draft | null {
  try {
    const parsed: unknown = JSON.parse(sessionStorage.getItem(STORAGE_KEY) ?? 'null');
    if (isDraft(parsed)) return { answers: { ...NO_ANSWER, ...parsed.answers }, finished: parsed.finished };
    return null;
  } catch {
    return inMemory;
  }
}

export function saveDraft(draft: Draft | null): void {
  inMemory = draft;
  try {
    if (draft) sessionStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
    else sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // Kept in memory only.
  }
}

function isDraft(value: unknown): value is Draft {
  return (
    typeof value === 'object' &&
    value !== null &&
    'answers' in value &&
    typeof value.answers === 'object' &&
    value.answers !== null &&
    'finished' in value &&
    typeof value.finished === 'boolean'
  );
}
