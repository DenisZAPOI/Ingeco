import { t } from '../../i18n';
import { PageHero } from '../layout/PageHero';

type StepHeaderProps = { step: number; total: number; title: string };

/** Where the user is in the booking: "Étape 2 sur 4", the question of the
 *  step, and a bar filled up to it (the text already says it for a screen reader). */
export function StepHeader({ step, total, title }: StepHeaderProps) {
  return (
    <PageHero eyebrow={t('booking.step', { step, total })} title={title}>
      <div className="progress" aria-hidden="true">
        {Array.from({ length: total }, (_, index) => (
          <span key={index} className={index < step ? 'progress-step progress-step-done' : 'progress-step'} />
        ))}
      </div>
    </PageHero>
  );
}
