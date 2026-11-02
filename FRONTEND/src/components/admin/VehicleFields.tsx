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
        label="Immatriculation"
        value={draft.plate}
        onChange={(plate) => onChange({ ...draft, plate })}
        autoCapitalize="characters"
        hint="Exemple : AB-123-CD"
        required
        error={error('plate')}
      />
      <TextField
        label="Marque et modèle"
        value={draft.model}
        onChange={(model) => onChange({ ...draft, model })}
        hint="Tel que le passager le verra. Exemple : Renault Kangoo blanche"
        required
        error={error('model')}
      />
      <TextField
        label="Nombre de places passagers"
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
        label="Véhicule adapté au fauteuil roulant"
        checked={draft.isAccessible}
        onChange={(isAccessible) => onChange({ ...draft, isAccessible })}
        error={error('isAccessible')}
      />
    </>
  );
}
