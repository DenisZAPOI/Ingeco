import { useId, useState } from 'react';
import { Navigate, useNavigate, useParams } from 'react-router-dom';

import { saveQuestionnaire, type Answers } from '../api/orientation';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { useSession } from '../hooks/useSession';
import { useSubmit } from '../hooks/useSubmit';
import { t } from '../i18n';
import {
  EXPERIENCE_TEXT_MAX_LENGTH,
  NO_ANSWER,
  QUESTIONS,
  chosen,
  readDraft,
  saveDraft,
  toggle,
  type Question,
} from '../lib/orientation';
import { ORIENTATION_PATH, ORIENTATION_PLAN_PATH, orientationQuestionPath } from '../lib/paths';

/** One question of the orientation questionnaire, as large tiles (module M1).
 *  The answers live in sessionStorage until the plan: they survive a reload
 *  and the phone's Back button. */
export function OrientationQuestionPage() {
  const number = Number(useParams().number);
  const q = QUESTIONS[number - 1];
  if (!q) {
    return <Navigate to={ORIENTATION_PATH} replace />;
  }
  // key: a new question starts from its own stored answers.
  return <QuestionScreen key={number} number={number} question={q} />;
}

function QuestionScreen({ number, question }: { number: number; question: Question }) {
  const navigate = useNavigate();
  const { user, hint } = useSession();
  const [answers, setAnswers] = useState<Answers>(() => readDraft()?.answers ?? NO_ANSWER);
  const save = useSubmit(saveQuestionnaire);
  const name = useId();
  const total = QUESTIONS.length;
  const last = number === total;
  const picked = chosen(answers, question.field);
  const title = t(`orientation.questions.${question.field}.title`);
  const field = question.field;
  // The single-choice questions need no hint under their title.
  const isSingleChoice = field === 'situation' || field === 'project' || field === 'french';
  const questionHint = isSingleChoice ? null : t(`orientation.questions.${field}.hint`);

  function change(next: Answers) {
    setAnswers(next);
    saveDraft({ answers: next, finished: false });
  }

  async function next() {
    if (!last) {
      navigate(orientationQuestionPath(number + 1));
      return;
    }
    // A rider's plan is kept at once; anyone else's is computed on the plan page.
    if ((user ?? hint)?.role === 'rider') {
      const plan = await save.submit(answers);
      if (!plan) return;
      saveDraft(null);
      navigate(ORIENTATION_PLAN_PATH, { state: { plan } });
      return;
    }
    saveDraft({ answers, finished: true });
    navigate(ORIENTATION_PLAN_PATH);
  }

  return (
    <section>
      <PageHero
        eyebrow={t('orientation.questionNumber', { number, total })}
        title={title}
      >
        <div className="progress" aria-hidden="true">
          {QUESTIONS.map((other, index) => (
            <span key={other.field} className={index < number ? 'progress-step progress-step-done' : 'progress-step'} />
          ))}
        </div>
      </PageHero>
      <PageSheet>
        {questionHint && <p className="note">{questionHint}</p>}
        <fieldset className="field choices">
          <legend className="visually-hidden">{title}</legend>
          {question.choices.map((code) => (
            <label key={code} className="choice">
              <input
                type={question.multiple ? 'checkbox' : 'radio'}
                name={name}
                value={code}
                checked={picked.includes(code)}
                onChange={(event) => change(toggle(answers, question, code, event.target.checked))}
              />
              <span className="choice-text">
                {t(`orientation.answers.${code}`)}
                {isHinted(code) && <span className="choice-hint">{t(`orientation.answerHints.${code}`)}</span>}
              </span>
            </label>
          ))}
        </fieldset>
        {question.field === 'experiences' && (
          <div className="field">
            <label htmlFor={`${name}-free`} className="field-label">
              {t('orientation.freeLabel')}
            </label>
            <p className="field-hint">{t('orientation.freeHint')}</p>
            <textarea
              id={`${name}-free`}
              className="field-input field-textarea"
              value={answers.experienceText ?? ''}
              maxLength={EXPERIENCE_TEXT_MAX_LENGTH}
              onChange={(event) => change({ ...answers, experienceText: event.target.value || null })}
            />
          </div>
        )}
        {save.error && (
          <p role="alert" className="alert alert-error">
            {save.error}
          </p>
        )}
        <div className="stack">
          <button type="button" className="button button-block" onClick={next} disabled={save.submitting}>
            {last ? t('orientation.seePlan') : t('orientation.next')}
          </button>
          {picked.length === 0 && (
            <button type="button" className="button button-block button-secondary" onClick={next} disabled={save.submitting}>
              {t('orientation.skip')}
            </button>
          )}
          <button
            type="button"
            className="link-button"
            onClick={() => navigate(number === 1 ? ORIENTATION_PATH : orientationQuestionPath(number - 1))}
          >
            {t('orientation.back')}
          </button>
        </div>
      </PageSheet>
    </section>
  );
}

/** The answers that have a second line under their label (keys of orientation.answerHints). */
const HINTED = ['reprise', 'trajet', 'vehicule_adapte'] as const;

function isHinted(code: string): code is (typeof HINTED)[number] {
  return (HINTED as readonly string[]).includes(code);
}
