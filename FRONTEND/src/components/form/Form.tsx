import { useEffect, useRef, type FormEvent, type ReactNode } from 'react';

type FormProps = {
  onSubmit: () => void;
  submitLabel: string;
  submitting: boolean;
  /** General message of the last failure. */
  error: string | null;
  /** Shown above the button after a success (profile saved…). */
  success?: string | null;
  children: ReactNode;
};

/** A form with its general message and its large submit button. */
export function Form({ onSubmit, submitLabel, submitting, error, success, children }: FormProps) {
  const messageRef = useRef<HTMLDivElement>(null);

  // Move the focus to the message: a screen reader announces it, and on a
  // small screen the user sees it instead of a button that "did nothing".
  useEffect(() => {
    if (error || success) {
      messageRef.current?.focus();
    }
  }, [error, success]);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form className="form" onSubmit={handleSubmit} noValidate>
      {children}
      <div ref={messageRef} tabIndex={-1}>
        {error && (
          <p role="alert" className="alert alert-error">
            {error}
          </p>
        )}
        {success && (
          <p role="status" className="alert alert-success">
            {success}
          </p>
        )}
      </div>
      <button type="submit" className="button button-block" disabled={submitting}>
        {submitting ? 'Envoi en cours…' : submitLabel}
      </button>
    </form>
  );
}
