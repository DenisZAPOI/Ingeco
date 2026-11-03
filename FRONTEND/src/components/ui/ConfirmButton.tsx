import { useEffect, useRef, useState, type ReactNode } from 'react';

import { useSlowNetwork } from '../../hooks/useSlowNetwork';
import { t } from '../../i18n';

type ConfirmButtonProps = {
  /** The button before confirmation ("Annuler ce trajet"). */
  label: string;
  question: string;
  /** Under the question: what will happen (refund, ride offered again…). */
  details?: ReactNode;
  confirmLabel: string;
  keepLabel: string;
  submitting: boolean;
  error: string | null;
  onConfirm: () => void;
};

/** A serious action confirmed on the spot: no pop-up window to find or close.
 *  The question takes the focus, so a screen reader reads it at once. */
export function ConfirmButton({ label, question, details, confirmLabel, keepLabel, submitting, error, onConfirm }: ConfirmButtonProps) {
  const [confirming, setConfirming] = useState(false);
  const slow = useSlowNetwork(submitting);
  const questionRef = useRef<HTMLParagraphElement>(null);

  useEffect(() => {
    if (confirming) questionRef.current?.focus();
  }, [confirming]);

  if (!confirming) {
    return (
      <button type="button" className="button button-block button-secondary" onClick={() => setConfirming(true)}>
        {label}
      </button>
    );
  }

  return (
    <div className="panel confirm">
      <p ref={questionRef} tabIndex={-1} className="confirm-question">
        {question}
      </p>
      {details}
      {error && (
        <p role="alert" className="alert alert-error">
          {error}
        </p>
      )}
      {slow && (
        <p role="status" className="note">
          {t('common.sendingSlow')}
        </p>
      )}
      <div className="stack">
        <button type="button" className="button button-block" onClick={onConfirm} disabled={submitting}>
          {submitting ? t('common.sending') : confirmLabel}
        </button>
        <button
          type="button"
          className="button button-block button-secondary"
          onClick={() => setConfirming(false)}
          disabled={submitting}
        >
          {keepLabel}
        </button>
      </div>
    </div>
  );
}
