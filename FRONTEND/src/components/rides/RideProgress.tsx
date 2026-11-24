import type { RideStatus } from '../../api/rides';
import { t } from '../../i18n';
import { RIDE_PROGRESS_STEPS, rideStepsReached } from '../../lib/rideProgress';

/** Where a trip stands: a bar in four segments, then one line in words
 *  ("Étape 2 sur 4 : Chauffeur trouvé"), so the color is never the only sign
 *  and four labels never have to fit side by side on a phone. Nothing for a
 *  trip off the path (cancelled, expired): its status says it. Updated with
 *  the status, in real time on the trip page; no position of the driver. */
export function RideProgress({ status }: { status: RideStatus }) {
  const reached = rideStepsReached(status);
  if (reached === null) return null;

  const currentStep = RIDE_PROGRESS_STEPS[reached - 1];
  const summary = t('ride.progress.summary', {
    step: reached,
    total: RIDE_PROGRESS_STEPS.length,
    label: t(`ride.progress.${currentStep}`),
  });

  return (
    <div className="ride-progress">
      {/* Read by screen readers step by step; the line below says the same to the eye. */}
      <ol className="ride-progress-bar" aria-label={t('ride.progress.label')}>
        {RIDE_PROGRESS_STEPS.map((step, index) => {
          const isReached = index < reached;
          const isCurrent = index === reached - 1;
          return (
            <li
              key={step}
              className={isReached ? 'ride-progress-step ride-progress-done' : 'ride-progress-step'}
              aria-current={isCurrent ? 'step' : undefined}
            >
              <span className="visually-hidden">
                {t(`ride.progress.${step}`)}
                {isReached && <span> {t('ride.progress.reached')}</span>}
              </span>
            </li>
          );
        })}
      </ol>
      <p className="ride-progress-text" aria-hidden="true">
        {summary}
      </p>
    </div>
  );
}
