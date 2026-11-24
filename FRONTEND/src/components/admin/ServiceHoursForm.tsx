import { useState } from 'react';

import type { Week } from '../../api/settings';
import { useSaveServiceHours, useServiceHours } from '../../hooks/useSettings';
import { t } from '../../i18n';
import { DAY_NAME_KEYS, dayForms, weekBody, type DayForm } from '../../lib/settings';
import { CheckboxField } from '../form/CheckboxField';
import { Form } from '../form/Form';
import { TextField } from '../form/TextField';
import { RequestState } from '../ui/RequestState';

/** When a ride can be requested: one slot per day, or closed (§5 M9, §18). */
export function ServiceHoursForm() {
  const hours = useServiceHours();

  return (
    <section>
      <h2>{t('settings.hoursTitle')}</h2>
      <p className="note">{t('settings.hoursNote')}</p>
      <RequestState loading={hours.loading} error={hours.error} onRetry={hours.retry}>
        {hours.data && <WeekFields week={hours.data} />}
      </RequestState>
    </section>
  );
}

function WeekFields({ week }: { week: Week }) {
  const [days, setDays] = useState(() => dayForms(week.days));
  const [saved, setSaved] = useState(false);
  const save = useSaveServiceHours();

  function change(index: number, changes: Partial<DayForm>) {
    setSaved(false);
    setDays((previous) => previous.map((day, position) => (position === index ? { ...day, ...changes } : day)));
  }

  async function submit() {
    const result = await save.submit(weekBody(days));
    if (!result) return;
    setDays(dayForms(result.days));
    setSaved(true);
  }

  return (
    <Form
      onSubmit={submit}
      submitLabel={t('settings.hoursSubmit')}
      submitting={save.submitting}
      error={save.error}
      success={saved ? t('settings.hoursSaved') : null}
    >
      {days.map((day, index) => (
        <DayFields key={day.weekday} day={day} error={save.errors[`days.${index}`]} onChange={(changes) => change(index, changes)} />
      ))}
    </Form>
  );
}

type DayFieldsProps = {
  day: DayForm;
  error?: string;
  onChange: (changes: Partial<DayForm>) => void;
};

function DayFields({ day, error, onChange }: DayFieldsProps) {
  return (
    <fieldset className="field panel">
      <legend className="field-label">{t(DAY_NAME_KEYS[day.weekday])}</legend>
      <CheckboxField label={t('settings.closed')} checked={day.closed} onChange={(closed) => onChange({ closed })} />
      {!day.closed && (
        <div className="field-pair">
          <TextField type="time" label={t('settings.opensAt')} value={day.opensAt} onChange={(opensAt) => onChange({ opensAt })} />
          <TextField
            type="time"
            label={t('settings.closesAt')}
            hint={t('settings.closesAtHint')}
            value={day.closesAt}
            onChange={(closesAt) => onChange({ closesAt })}
          />
        </div>
      )}
      {error && (
        <p role="alert" className="field-error">
          {error}
        </p>
      )}
    </fieldset>
  );
}
