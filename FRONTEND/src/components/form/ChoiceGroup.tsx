import { useId } from 'react';

export type Choice<Value extends string> = { value: Value; label: string };

type ChoiceGroupProps<Value extends string> = {
  legend: string;
  choices: readonly Choice<Value>[];
  value: Value | null;
  onChange: (value: Value) => void;
  error?: string;
};

/** Radio buttons as large tiles: every choice visible at once, the whole tile touchable. */
export function ChoiceGroup<Value extends string>({ legend, choices, value, onChange, error }: ChoiceGroupProps<Value>) {
  const name = useId();
  const errorId = `${name}-error`;

  return (
    <fieldset className="field choices" aria-describedby={error ? errorId : undefined}>
      <legend className="field-label">{legend}</legend>
      {choices.map((choice) => (
        <label key={choice.value} className="choice">
          <input
            type="radio"
            name={name}
            value={choice.value}
            checked={value === choice.value}
            onChange={() => onChange(choice.value)}
          />
          {choice.label}
        </label>
      ))}
      {error && (
        <p id={errorId} className="field-error">
          {error}
        </p>
      )}
    </fieldset>
  );
}
