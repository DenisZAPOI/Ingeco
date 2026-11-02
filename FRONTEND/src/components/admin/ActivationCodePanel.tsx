import { useEffect, useRef } from 'react';

import type { ActivationCode } from '../../api/admin';
import { formatActivationCode } from '../../lib/accounts';
import { formatDateTime } from '../../lib/format';
import { formatPhone } from '../../lib/phone';

type ActivationCodePanelProps = {
  activation: ActivationCode;
  firstName: string;
  phone: string;
};

/** The code, shown once: it cannot be read again, only replaced. Takes the
 *  focus, so a screen reader reads it at once. */
export function ActivationCodePanel({ activation, firstName, phone }: ActivationCodePanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    panelRef.current?.focus();
  }, [activation.code]);

  return (
    <div ref={panelRef} tabIndex={-1} className="panel activation-code" role="status">
      <p>Code d'activation de {firstName} :</p>
      <p className="activation-code-value">{formatActivationCode(activation.code)}</p>
      <p>
        Donnez-le par téléphone ou en main propre. Avec ce code et son numéro ({formatPhone(phone)}), {firstName} choisit
        son mot de passe dans « J'ai reçu un code ».
      </p>
      <p className="note">
        Valable jusqu'au {formatDateTime(activation.expiresAt)}. Notez-le maintenant : il ne sera plus affiché. Un nouveau
        code remplacera celui-ci.
      </p>
    </div>
  );
}
