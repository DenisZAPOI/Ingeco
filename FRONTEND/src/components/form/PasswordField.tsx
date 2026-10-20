import { useId, useState } from 'react';

import { PASSWORD_RULES } from '../../lib/passwordRules';

type PasswordFieldProps = {
  label: string;
  value: string;
  onChange: (value: string) => void;
  /** "new-password" also shows the rules, checked as the user types. */
  autoComplete: 'current-password' | 'new-password';
  error?: string;
};

export function PasswordField({ label, value, onChange, autoComplete, error }: PasswordFieldProps) {
  const id = useId();
  const rulesId = `${id}-rules`;
  const errorId = `${id}-error`;
  // Typing a password with a capital, a digit and a symbol on a phone without
  // seeing it leads to mistakes: the user can show it.
  const [visible, setVisible] = useState(false);
  const isNew = autoComplete === 'new-password';
  const describedBy = [isNew && rulesId, error && errorId].filter(Boolean).join(' ') || undefined;

  return (
    <div className="field">
      <label htmlFor={id} className="field-label">
        {label}
      </label>
      <div className="password-input">
        <input
          id={id}
          className="field-input"
          type={visible ? 'text' : 'password'}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          autoComplete={autoComplete}
          autoCapitalize="none"
          spellCheck={false}
          required
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
        />
        <button
          type="button"
          className="button button-secondary"
          onClick={() => setVisible((shown) => !shown)}
          aria-pressed={visible}
        >
          {visible ? 'Masquer' : 'Afficher'}
        </button>
      </div>
      {isNew && (
        <ul id={rulesId} className="password-rules">
          {PASSWORD_RULES.map((rule) => {
            const met = rule.isMet(value);
            return (
              <li key={rule.label} className={met ? 'rule-met' : undefined}>
                <span aria-hidden="true">{met ? '✓' : '•'}</span> {rule.label}
                <span className="visually-hidden">{met ? ' : fait' : ' : à faire'}</span>
              </li>
            );
          })}
        </ul>
      )}
      {error && (
        <p id={errorId} className="field-error">
          {error}
        </p>
      )}
    </div>
  );
}
