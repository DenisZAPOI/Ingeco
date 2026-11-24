import { useState } from 'react';

import type { Week } from '../../api/settings';
import { useSaveServiceHours, useServiceHours } from '../../hooks/useSettings';
import { t } from '../../i18n';
import type { FieldErrors } from '../../lib/fieldErrors';
import {
  DAY_NAME_KEYS,
  DAY_SHORT_KEYS,
  dayForms,
  firstOpenDay,
  hasSameHours,
  weekBody,
  withCommonHours,
  type DayForm,
  type Weekday,
} from '../../lib/settings';
import { Form } from '../form/Form';
import { TextField } from '../form/TextField';
import { ArrowRightIcon, CheckIcon } from '../ui/icons';
import { RequestState } from '../ui/RequestState';

/** When a ride can be requested: the open days, then one slot for all of
 *  them, or one per day (§5 M9, §18). */
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
  // Opened already when the days differ in the database: nothing is hidden.
  const [perDay, setPerDay] = useState(() => !hasSameHours(dayForms(week.days)));
  // The day whose hours were just given to every day, to say so before saving.
  const [unifiedFrom, setUnifiedFrom] = useState<Weekday | null>(null);
  const [saved, setSaved] = useState(false);
  const save = useSaveServiceHours();

  function changeDay(weekday: Weekday, changes: Partial<DayForm>) {
    setSaved(false);
    setDays((previous) => previous.map((day) => (day.weekday === weekday ? { ...day, ...changes } : day)));
  }

  function changeCommon(opensAt: string, closesAt: string) {
    setSaved(false);
    setDays((previous) => withCommonHours(previous, opensAt, closesAt));
  }

  function showSameHours() {
    setPerDay(false);
    const first = firstOpenDay(days);
    if (first === null || hasSameHours(days)) return;
    // The hours of the first open day go to every day: said before saving.
    setDays(withCommonHours(days, first.opensAt, first.closesAt));
    setUnifiedFrom(first.weekday);
  }

  async function submit() {
    const result = await save.submit(weekBody(days));
    if (!result) return;
    setDays(dayForms(result.days));
    setUnifiedFrom(null);
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
      <DayToggles days={days} onToggle={(weekday, open) => changeDay(weekday, { closed: !open })} />
      {perDay ? (
        <PerDayHours days={days} errors={save.errors} onChange={changeDay} />
      ) : (
        <CommonHours days={days} errors={save.errors} onChange={changeCommon} />
      )}
      {unifiedFrom !== null && (
        <p role="status" className="alert alert-info">
          {t('settings.unifiedNote', { day: t(DAY_NAME_KEYS[unifiedFrom]) })}
        </p>
      )}
      <button type="button" className="link-button" onClick={perDay ? showSameHours : () => setPerDay(true)}>
        {perDay ? t('settings.sameHoursToggle') : t('settings.perDayToggle')}
      </button>
    </Form>
  );
}

type DayTogglesProps = {
  days: DayForm[];
  onToggle: (weekday: Weekday, open: boolean) => void;
};

/** One button per day, ticked when the service is open: a tick, not only a colour. */
function DayToggles({ days, onToggle }: DayTogglesProps) {
  return (
    <fieldset className="field choices">
      <legend className="field-label">{t('settings.openDaysLegend')}</legend>
      <div className="day-toggles">
        {days.map((day) => (
          <label key={day.weekday} className="day-toggle">
            <input type="checkbox" checked={!day.closed} onChange={(event) => onToggle(day.weekday, event.target.checked)} />
            {!day.closed && <CheckIcon className="day-toggle-tick" />}
            <span aria-hidden="true">{t(DAY_SHORT_KEYS[day.weekday])}</span>
            <span className="visually-hidden">{t(DAY_NAME_KEYS[day.weekday])}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}

type HoursProps = {
  days: DayForm[];
  errors: FieldErrors;
};

/** The first error of the week: in the common mode, every day has the same hours, so the same problem. */
function firstDayError(errors: FieldErrors, days: DayForm[]): string | undefined {
  const messages = days.map((_, index) => errors[`days.${index}`]).filter(Boolean);
  return messages[0];
}

function CommonHours({ days, errors, onChange }: HoursProps & { onChange: (opensAt: string, closesAt: string) => void }) {
  const first = firstOpenDay(days) ?? days[0];
  const error = firstDayError(errors, days);

  return (
    <div className="field">
      <div className="field-pair">
        <TextField type="time" label={t('settings.opensAt')} value={first.opensAt} onChange={(opensAt) => onChange(opensAt, first.closesAt)} />
        <TextField type="time" label={t('settings.closesAt')} value={first.closesAt} onChange={(closesAt) => onChange(first.opensAt, closesAt)} />
      </div>
      {error && (
        <p role="alert" className="field-error">
          {error}
        </p>
      )}
    </div>
  );
}

function PerDayHours({ days, errors, onChange }: HoursProps & { onChange: (weekday: Weekday, changes: Partial<DayForm>) => void }) {
  return (
    <div className="day-hours">
      {days.map((day, index) => {
        if (day.closed) return null;
        const dayName = t(DAY_NAME_KEYS[day.weekday]);
        const error = errors[`days.${index}`];
        return (
          <div key={day.weekday} className="day-hours-row">
            <span className="day-hours-name">{dayName}</span>
            <input
              type="time"
              className="field-input"
              aria-label={t('settings.opensAtOf', { day: dayName })}
              value={day.opensAt}
              onChange={(event) => onChange(day.weekday, { opensAt: event.target.value })}
            />
            <ArrowRightIcon className="day-hours-arrow" />
            <input
              type="time"
              className="field-input"
              aria-label={t('settings.closesAtOf', { day: dayName })}
              value={day.closesAt}
              onChange={(event) => onChange(day.weekday, { closesAt: event.target.value })}
            />
            {error && (
              <p role="alert" className="field-error day-hours-error">
                {error}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
