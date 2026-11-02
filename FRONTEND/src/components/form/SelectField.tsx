import { useId } from 'react';

import type { Choice } from './ChoiceGroup';

type SelectFieldProps<Value extends string> = {
  label: string;
  choices: readonly Choice<Value>[];
  value: Value;
  onChange: (value: Value) => void;
};

/** A drop-down list: for the many choices of a filter, where tiles would take the whole screen. */
export function SelectField<Value extends string>({ label, choices, value, onChange }: SelectFieldProps<Value>) {
  const id = useId();

  return (
    <div className="field">
      <label htmlFor={id} className="field-label">
        {label}
      </label>
      <select id={id} className="field-input" value={value} onChange={(event) => onChange(event.target.value as Value)}>
        {choices.map((choice) => (
          <option key={choice.value} value={choice.value}>
            {choice.label}
          </option>
        ))}
      </select>
    </div>
  );
}
