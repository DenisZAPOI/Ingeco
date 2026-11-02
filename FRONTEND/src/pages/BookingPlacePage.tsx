import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';

import type { Stop } from '../api/rides';
import { PageSheet } from '../components/layout/PageHero';
import { PlacePicker } from '../components/booking/PlacePicker';
import { StepHeader } from '../components/booking/StepHeader';
import { Form } from '../components/form/Form';
import { RequestState } from '../components/ui/RequestState';
import { useBookingDraft } from '../hooks/useBookingDraft';
import { useCommunes } from '../hooks/useCommunes';
import { CHECK_FIELDS } from '../lib/errorMessage';
import { BOOKING_PATHS } from '../lib/paths';

const STEPS = {
  pickup: { step: 1, title: "D'où partez-vous ?", next: BOOKING_PATHS.dropoff, back: null },
  dropoff: { step: 2, title: 'Où allez-vous ?', next: BOOKING_PATHS.time, back: BOOKING_PATHS.pickup },
} as const;

/** Steps 1 and 2: the pickup, then the drop-off. Each route gives it its own
 *  key: otherwise React would keep the pickup's state on the drop-off step. */
export function BookingPlacePage({ stop }: { stop: 'pickup' | 'dropoff' }) {
  const { draft, update } = useBookingDraft();
  const communes = useCommunes();
  const navigate = useNavigate();
  const [chosen, setChosen] = useState<Stop | null>(draft[stop]);
  const [error, setError] = useState<string | null>(null);
  const step = STEPS[stop];

  if (stop === 'dropoff' && !draft.pickup) {
    return <Navigate to={BOOKING_PATHS.pickup} replace />;
  }

  function next() {
    if (!chosen) {
      setError("Cherchez l'adresse, puis choisissez-la dans la liste.");
      return;
    }
    update({ [stop]: chosen });
    navigate(step.next);
  }

  return (
    <section>
      <StepHeader step={step.step} title={step.title} />
      <PageSheet>
        <RequestState loading={communes.loading} error={communes.error} onRetry={communes.retry}>
          <Form onSubmit={next} submitLabel="Continuer" submitting={false} error={error ? CHECK_FIELDS : null}>
            <PlacePicker
              communes={communes.data ?? []}
              value={chosen}
              onChange={(place) => {
                setChosen(place);
                setError(null);
              }}
              error={error ?? undefined}
            />
          </Form>
        </RequestState>
        {step.back && (
          <Link to={step.back} className="link-action">
            Revenir à l'étape précédente
          </Link>
        )}
      </PageSheet>
    </section>
  );
}
