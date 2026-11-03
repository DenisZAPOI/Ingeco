import { t } from '../../i18n';
import type { FieldErrors } from '../../lib/fieldErrors';
import { MAX_SEATS, MIN_SEATS, type VehicleDraft } from '../../lib/vehicle';
import { CheckboxField } from '../form/CheckboxField';
import { TextField } from '../form/TextField';

type VehicleFieldsProps = {
  draft: VehicleDraft;
  onChange: (draft: VehicleDraft) => void;
  errors: FieldErrors;
  /** Where the vehicle is in the request body ("vehicle"): the API names the faulty fields from it. */
  prefix: string;
};

/** The driver's vehicle, checked in person with their documents. */
export function VehicleFields({ draft, onChange, errors, prefix }: VehicleFieldsProps) {
  const error = (field: string) => errors[`${prefix}.${field}`];

  return (
    <>
      <TextField
        label={t('admin.plate')}
        value={draft.plate}
        onChange={(plate) => onChange({ ...draft, plate })}
        autoCapitalize="characters"
        hint={t('admin.plateHint')}
        required
        error={error('plate')}
      />
      <TextField
        label={t('admin.model')}
        value={draft.model}
        onChange={(model) => onChange({ ...draft, model })}
        hint={t('admin.modelHint')}
        required
        error={error('model')}
      />
      <TextField
        label={t('admin.seats')}
        value={draft.seats}
        onChange={(seats) => onChange({ ...draft, seats })}
        type="number"
        inputMode="numeric"
        min={MIN_SEATS}
        max={MAX_SEATS}
        required
        error={error('seats')}
      />
      <CheckboxField
        label={t('admin.accessibleVehicle')}
        checked={draft.isAccessible}
        onChange={(isAccessible) => onChange({ ...draft, isAccessible })}
        error={error('isAccessible')}
      />
    </>
  );
}
