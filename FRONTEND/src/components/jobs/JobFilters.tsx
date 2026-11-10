import { t } from '../../i18n';
import { NO_FILTER, SCHEDULES, scheduleLabel, type JobFilters as Filters } from '../../lib/jobs';
import { CheckboxField } from '../form/CheckboxField';
import { SelectField } from '../form/SelectField';

const ALL = 'all';

type JobFiltersProps = {
  communes: { id: number; name: string }[];
  value: Filters;
  onChange: (filters: Filters) => void;
};

/** Commune, hours, beginner, no diploma (cahier des charges §7.2). Every
 *  change filters at once: no "Filtrer" button, no wait. */
export function JobFilters({ communes, value, onChange }: JobFiltersProps) {
  const communeChoices = [
    { value: ALL, label: t('jobs.allCommunes') },
    ...communes.map((commune) => ({ value: String(commune.id), label: commune.name })),
  ];
  const scheduleChoices = [
    { value: ALL, label: t('jobs.allSchedules') },
    ...SCHEDULES.map((schedule) => ({ value: schedule, label: scheduleLabel(schedule) })),
  ];
  const active = JSON.stringify(value) !== JSON.stringify(NO_FILTER);

  return (
    <fieldset className="panel filters">
      <legend className="panel-title">{t('jobs.filtersTitle')}</legend>
      <SelectField
        label={t('jobs.commune')}
        choices={communeChoices}
        value={value.communeId === null ? ALL : String(value.communeId)}
        onChange={(chosen) => onChange({ ...value, communeId: chosen === ALL ? null : Number(chosen) })}
      />
      <SelectField
        label={t('jobs.scheduleLabel')}
        choices={scheduleChoices}
        value={value.schedule ?? ALL}
        onChange={(chosen) => onChange({ ...value, schedule: SCHEDULES.find((schedule) => schedule === chosen) ?? null })}
      />
      <CheckboxField
        label={t('jobs.beginnerWelcome')}
        checked={value.beginnerWelcome}
        onChange={(checked) => onChange({ ...value, beginnerWelcome: checked })}
      />
      <CheckboxField
        label={t('jobs.noDiplomaRequired')}
        checked={value.noDiplomaRequired}
        onChange={(checked) => onChange({ ...value, noDiplomaRequired: checked })}
      />
      {active && (
        <button type="button" className="link-button link-action" onClick={() => onChange(NO_FILTER)}>
          {t('jobs.clearFilters')}
        </button>
      )}
    </fieldset>
  );
}
