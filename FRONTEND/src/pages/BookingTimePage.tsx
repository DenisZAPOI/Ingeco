import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';

import type { Purpose } from '../api/rides';
import { PageSheet } from '../components/layout/PageHero';
import { StepHeader } from '../components/booking/StepHeader';
import { ChoiceGroup } from '../components/form/ChoiceGroup';
import { Form } from '../components/form/Form';
import { TextField } from '../components/form/TextField';
import { useBookingDraft } from '../hooks/useBookingDraft';
import { t } from '../i18n';
import type { When } from '../lib/bookingDraft';
import { guyanaToday } from '../lib/format';
import { BOOKING_PATHS } from '../lib/paths';
import { PURPOSES, purposeLabel, scheduleError } from '../lib/ride';

function whenChoices(): { value: When; label: string }[] {
  return [
    { value: 'now', label: t('booking.now') },
    { value: 'later', label: t('booking.later') },
  ];
}

function purposeChoices(): { value: Purpose; label: string }[] {
  return PURPOSES.map((purpose) => ({ value: purpose, label: purposeLabel(purpose) }));
}

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
      purpose: purpose ? undefined : t('booking.purposeMissing'),
      schedule: when === 'later' ? (scheduleError(day, time) ?? undefined) : undefined,
    };
    setErrors(found);
    if (found.purpose || found.schedule || !purpose) return;
    update({ purpose, when, day: when === 'later' ? day : '', time: when === 'later' ? time : '' });
    navigate(BOOKING_PATHS.confirm);
  }

  return (
    <section>
      <StepHeader step={3} title={t('booking.timeTitle')} />
      <PageSheet>
        <Form
          onSubmit={next}
          submitLabel={t('booking.seePrice')}
          submitting={false}
          error={errors.purpose || errors.schedule ? t('errors.checkFields') : null}
        >
          <ChoiceGroup legend={t('booking.purposeLegend')} choices={purposeChoices()} value={purpose} onChange={setPurpose} error={errors.purpose} />
          <ChoiceGroup legend={t('booking.whenLegend')} choices={whenChoices()} value={when} onChange={setWhen} />
          {when === 'later' && (
            <>
              <TextField label={t('booking.day')} type="date" value={day} onChange={setDay} min={guyanaToday()} required />
              <TextField
                label={t('booking.time')}
                hint={t('booking.timeHint')}
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
          {t('booking.previousStep')}
        </Link>
      </PageSheet>
    </section>
  );
}
