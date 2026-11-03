import { t } from '../../i18n';
import { PageHero } from '../layout/PageHero';

export const BOOKING_STEPS = 4;

type StepHeaderProps = { step: number; title: string };

/** Where the user is in the booking: "Étape 2 sur 4", the question of the
 *  step, and a bar filled up to it (the text already says it for a screen reader). */
export function StepHeader({ step, title }: StepHeaderProps) {
  return (
    <PageHero eyebrow={t('booking.step', { step, total: BOOKING_STEPS })} title={title}>
      <div className="progress" aria-hidden="true">
        {Array.from({ length: BOOKING_STEPS }, (_, index) => (
          <span key={index} className={index < step ? 'progress-step progress-step-done' : 'progress-step'} />
        ))}
      </div>
    </PageHero>
  );
}
