export const BOOKING_STEPS = 4;

type StepHeaderProps = { step: number; title: string };

/** Where the user is in the booking: "Étape 2 sur 4", then the question of the step. */
export function StepHeader({ step, title }: StepHeaderProps) {
  return (
    <>
      <p className="step-progress">
        Étape {step} sur {BOOKING_STEPS}
      </p>
      <h1>{title}</h1>
    </>
  );
}
