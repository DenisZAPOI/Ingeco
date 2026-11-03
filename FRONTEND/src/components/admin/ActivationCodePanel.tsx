import { useEffect, useRef } from 'react';

import type { ActivationCode } from '../../api/admin';
import { t } from '../../i18n';
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
      <p>{t('admin.codeOf', { name: firstName })}</p>
      <p className="activation-code-value">{formatActivationCode(activation.code)}</p>
      <p>{t('admin.codeHandOver', { phone: formatPhone(phone), name: firstName })}</p>
      <p className="note">{t('admin.codeValidity', { date: formatDateTime(activation.expiresAt) })}</p>
    </div>
  );
}
