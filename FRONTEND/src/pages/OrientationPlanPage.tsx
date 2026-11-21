import { useCallback, useRef } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';

import { ApiError } from '../api/client';
import { fetchPlan, markStep, previewPlan, saveQuestionnaire, type Plan, type PlanStep } from '../api/orientation';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { PhoneIcon } from '../components/ui/icons';
import { RequestState } from '../components/ui/RequestState';
import { useRequest } from '../hooks/useRequest';
import { useSession } from '../hooks/useSession';
import { useSubmit } from '../hooks/useSubmit';
import { t, tn } from '../i18n';
import { draftForPurpose, saveBookingDraft } from '../lib/bookingDraft';
import { readDraft, saveDraft, stepTarget } from '../lib/orientation';
import { BOOKING_PATHS, CALLBACK_PATH, ORIENTATION_KEEP_PATH, ORIENTATION_PATH, orientationQuestionPath } from '../lib/paths';

const NOT_FOUND = 404;

/** What the page shows: a rider's kept plan, a plan computed without keeping it, or none yet. */
type Shown = { kind: 'kept'; plan: Plan } | { kind: 'preview'; steps: PlanStep[] } | { kind: 'none' };

/** « Mon plan d'action » (module M1): 3 to 5 steps by simple rules, each leading
 *  to a screen of the app, and always a human contact. A proposal, never a
 *  decision (GDPR art. 22). */
export function OrientationPlanPage() {
  const { user, hint } = useSession();
  const location = useLocation();
  const role = (user ?? hint)?.role ?? null;
  const isRider = role === 'rider';
  const draft = readDraft();
  const finished = draft?.finished ? draft : null;
  const justSaved = planFromState(location.state);
  // The rider came back from the login of « Garder mon plan »: the answers are
  // kept once, even when React runs the effect twice.
  const saving = useRef<Promise<Plan> | null>(null);

  const load = useCallback(async (): Promise<Shown> => {
    if (isRider && finished) {
      saving.current ??= saveQuestionnaire(finished.answers);
      const plan = await saving.current;
      saveDraft(null);
      return { kind: 'kept', plan };
    }
    if (isRider) {
      try {
        return { kind: 'kept', plan: await fetchPlan() };
      } catch (error) {
        if (error instanceof ApiError && error.status === NOT_FOUND) return { kind: 'none' };
        throw error;
      }
    }
    return finished ? { kind: 'preview', steps: await previewPlan(finished.answers) } : { kind: 'none' };
    // `finished` is read again at each call: only who is logged in changes the request.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isRider]);
  const shown = useRequest(load, justSaved ? { kind: 'kept', plan: justSaved } : null);

  // A visitor without answers has no plan to see: back to the start.
  if (!isRider && !finished && !justSaved) {
    return <Navigate to={ORIENTATION_PATH} replace />;
  }

  return (
    <section>
      <PlanContent shown={shown.data} role={role} loading={shown.loading && !shown.data} error={shown.error} onRetry={shown.retry} onChange={(plan) => shown.setData({ kind: 'kept', plan })} />
    </section>
  );
}

type PlanContentProps = {
  shown: Shown | null;
  role: string | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
  onChange: (plan: Plan) => void;
};

function PlanContent({ shown, role, loading, error, onRetry, onChange }: PlanContentProps) {
  const navigate = useNavigate();
  const steps = shown?.kind === 'kept' ? shown.plan.steps : shown?.kind === 'preview' ? shown.steps : [];
  const done = steps.filter((step) => step.doneAt !== null).length;

  function changeAnswers() {
    // A kept plan starts from its answers; a plan not kept, from the ones still on the phone.
    const answers = shown?.kind === 'kept' ? shown.plan.answers : readDraft()?.answers;
    if (answers) saveDraft({ answers, finished: false });
    navigate(orientationQuestionPath(1));
  }

  return (
    <>
      <PageHero title={t('orientation.planTitle')}>
        {steps.length > 0 && <p className="hero-lead">{tn('orientation.planLead', steps.length)}</p>}
      </PageHero>
      <PageSheet>
        <RequestState loading={loading} error={error} onRetry={onRetry}>
          {shown?.kind === 'none' ? (
            <>
              <p>{t('orientation.noPlan')}</p>
              <Link to={ORIENTATION_PATH} className="button button-block">
                {t('orientation.start')}
              </Link>
            </>
          ) : (
            <>
              <p className="note">{t('orientation.planProposal')}</p>
              {shown?.kind === 'kept' && (
                <p aria-live="polite">{tn('orientation.planDone', done, { total: steps.length })}</p>
              )}
              <ol className="plan-steps">
                {steps.map((step) => (
                  <PlanStepCard key={step.position} step={step} canTick={shown?.kind === 'kept'} onChange={onChange} />
                ))}
              </ol>
              <div className="panel">
                <h2 className="panel-title">{t('orientation.talkTitle')}</h2>
                <p>{t('orientation.talkText')}</p>
                <Link to={CALLBACK_PATH} state={{ fromPlan: true }} className="button button-block button-secondary">
                  <PhoneIcon className="button-icon" />
                  {t('orientation.callMe')}
                </Link>
              </div>
              {shown?.kind === 'kept' ? (
                <p className="note">{t('orientation.kept')}</p>
              ) : role === null ? (
                <Link to={ORIENTATION_KEEP_PATH} className="button button-block">
                  {t('orientation.keepPlan')}
                </Link>
              ) : (
                <p className="note">{t('orientation.notKeptOtherRole')}</p>
              )}
              <button type="button" className="link-button" onClick={changeAnswers}>
                {t('orientation.changeAnswers')}
              </button>
            </>
          )}
        </RequestState>
      </PageSheet>
    </>
  );
}

type PlanStepCardProps = { step: PlanStep; canTick: boolean; onChange: (plan: Plan) => void };

/** One step: what to do, the button that leads there, and « C'est fait » for a kept plan. */
function PlanStepCard({ step, canTick, onChange }: PlanStepCardProps) {
  const navigate = useNavigate();
  const tick = useSubmit((done: boolean) => markStep(step.position, done));
  const isDone = step.doneAt !== null;

  async function toggle(done: boolean) {
    // Shown ticked only once the API has kept it: never a false confirmation.
    const plan = await tick.submit(done);
    if (plan) onChange(plan);
  }

  function bookRide() {
    // The booking starts with the purpose « Emploi »: only the places and the time are left.
    saveBookingDraft(draftForPurpose('employment'));
    navigate(BOOKING_PATHS.pickup);
  }

  return (
    <li className={isDone ? 'plan-step plan-step-done' : 'plan-step'}>
      <h2 className="plan-step-title">
        {t(`orientation.steps.${step.code}.title`)}
        {isDone && <span className="badge">{t('orientation.stepDoneBadge')}</span>}
      </h2>
      <p>{t(`orientation.steps.${step.code}.text`)}</p>
      {step.code === 'trajet' ? (
        <button type="button" className="button button-block button-secondary" onClick={bookRide}>
          {t(`orientation.steps.${step.code}.action`)}
        </button>
      ) : (
        <Link
          to={stepTarget(step.code)}
          state={step.code === 'conseiller' ? { fromPlan: true } : undefined}
          className="button button-block button-secondary"
        >
          {t(`orientation.steps.${step.code}.action`)}
        </Link>
      )}
      {canTick && (
        <label className="checkbox">
          <input type="checkbox" checked={isDone} disabled={tick.submitting} onChange={(event) => toggle(event.target.checked)} />
          {t('orientation.stepDone')}
        </label>
      )}
      {tick.error && (
        <p role="alert" className="field-error">
          {tick.error}
        </p>
      )}
    </li>
  );
}

/** The plan handed over by the last question, just kept for a rider. */
function planFromState(state: unknown): Plan | null {
  if (typeof state !== 'object' || state === null || !('plan' in state)) return null;
  const { plan } = state as { plan: unknown };
  return typeof plan === 'object' && plan !== null && 'steps' in plan ? (plan as Plan) : null;
}
