import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';

import type { Purpose } from '../api/rides';
import { PageSheet } from '../components/layout/PageHero';
import { StepHeader } from '../components/booking/StepHeader';
import { ChoiceGroup } from '../components/form/ChoiceGroup';
import { Form } from '../components/form/Form';
import { TextField } from '../components/form/TextField';
import { useBookingDraft } from '../hooks/useBookingDraft';
import type { When } from '../lib/bookingDraft';
import { guyanaToday } from '../lib/format';
import { CHECK_FIELDS } from '../lib/errorMessage';
import { BOOKING_PATHS } from '../lib/paths';
import { PURPOSE_LABELS, PURPOSES, scheduleError } from '../lib/ride';

const WHEN_CHOICES = [
  { value: 'now', label: 'Maintenant' },
  { value: 'later', label: 'Plus tard (dans 30 minutes ou plus)' },
] as const satisfies readonly { value: When; label: string }[];

const PURPOSE_CHOICES = PURPOSES.map((purpose) => ({ value: purpose, label: PURPOSE_LABELS[purpose] }));

/** Step 3: why, and when. */
export function BookingTimePage() {
  const { draft, update } = useBookingDraft();
  const navigate = useNavigate();
  const [purpose, setPurpose] = useState<Purpose | null>(draft.purpose);
  const [when, setWhen] = useState<When>(draft.when);
  const [day, setDay] = useState(draft.day || guyanaToday());
  const [time, setTime] = useState(draft.time);
  const [errors, setErrors] = useState<{ purpose?: string; schedule?: string }>({});

  if (!draft.pickup || !draft.dropoff) {
    return <Navigate to={draft.pickup ? BOOKING_PATHS.dropoff : BOOKING_PATHS.pickup} replace />;
  }

  function next() {
    const found = {
      purpose: purpose ? undefined : 'Choisissez le motif du trajet.',
      schedule: when === 'later' ? (scheduleError(day, time) ?? undefined) : undefined,
    };
    setErrors(found);
    if (found.purpose || found.schedule || !purpose) return;
    update({ purpose, when, day: when === 'later' ? day : '', time: when === 'later' ? time : '' });
    navigate(BOOKING_PATHS.confirm);
  }

  return (
    <section>
      <StepHeader step={3} title="Pourquoi et quand ?" />
      <PageSheet>
        <Form
          onSubmit={next}
          submitLabel="Voir le prix"
          submitting={false}
          error={errors.purpose || errors.schedule ? CHECK_FIELDS : null}
        >
          <ChoiceGroup legend="Motif du trajet" choices={PURPOSE_CHOICES} value={purpose} onChange={setPurpose} error={errors.purpose} />
          <ChoiceGroup legend="Départ" choices={WHEN_CHOICES} value={when} onChange={setWhen} />
          {when === 'later' && (
            <>
              <TextField label="Jour" type="date" value={day} onChange={setDay} min={guyanaToday()} required />
              <TextField
                label="Heure de départ"
                hint="Heure de Guyane."
                type="time"
                value={time}
                onChange={setTime}
                required
                error={errors.schedule}
              />
            </>
          )}
        </Form>
        <Link to={BOOKING_PATHS.dropoff} className="link-action">
          Revenir à l'étape précédente
        </Link>
      </PageSheet>
    </section>
  );
}
