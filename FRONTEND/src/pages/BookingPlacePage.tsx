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
import { t } from '../i18n';
import { bookingSteps, NO_GIVEN_DROPOFF, skipsDropoff } from '../lib/bookingDraft';
import { BOOKING_PATHS } from '../lib/paths';

const STEPS = {
  pickup: { title: 'booking.pickupTitle', next: BOOKING_PATHS.dropoff, back: null },
  dropoff: { title: 'booking.dropoffTitle', next: BOOKING_PATHS.time, back: BOOKING_PATHS.pickup },
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
  const numbers = bookingSteps(draft);
  // From a job offer or a help service, the drop-off is already known: straight to the time.
  const toGiven = stop === 'pickup' && skipsDropoff(draft);

  if (stop === 'dropoff' && !draft.pickup) {
    return <Navigate to={BOOKING_PATHS.pickup} replace />;
  }

  function next() {
    if (!chosen) {
      setError(t('booking.chooseAddress'));
      return;
    }
    // A drop-off chosen here is no longer the one given: the usual 4 steps.
    update(stop === 'dropoff' ? { dropoff: chosen, ...NO_GIVEN_DROPOFF } : { pickup: chosen });
    navigate(toGiven ? BOOKING_PATHS.time : step.next);
  }

  function otherDestination() {
    update(NO_GIVEN_DROPOFF);
    navigate(BOOKING_PATHS.dropoff);
  }

  return (
    <section>
      <StepHeader step={numbers[stop]} total={numbers.total} title={t(step.title)} />
      <PageSheet>
        {toGiven && draft.dropoff && (
          <p className="note">
            {t(draft.helpServiceId !== null ? 'booking.toHelpService' : 'booking.toJob', { address: draft.dropoff.address })}
          </p>
        )}
        <RequestState loading={communes.loading} error={communes.error} onRetry={communes.retry}>
          <Form onSubmit={next} submitLabel={t('booking.continue')} submitting={false} error={error ? t('errors.checkFields') : null}>
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
        {toGiven && (
          <button type="button" className="link-button link-action" onClick={otherDestination}>
            {t('booking.otherDestination')}
          </button>
        )}
        {step.back && (
          <Link to={step.back} className="link-action">
            {t('booking.previousStep')}
          </Link>
        )}
      </PageSheet>
    </section>
  );
}
