import { t } from '../../i18n';
import { formatPhone } from '../../lib/phone';
import { PhoneIcon } from '../ui/icons';

// Given by the client, in international format (+594…). Until then the block
// stays hidden: a wrong number would be worse than none.
const CALL_CENTER_PHONE: string | null = import.meta.env.VITE_CALL_CENTER_PHONE || null;

/** The call center: its number in full, and a button to call it. */
export function CallCenterHelp() {
  if (!CALL_CENTER_PHONE) return null;
  return (
    <div className="panel help">
      <h2>{t('helpPage.callTitle')}</h2>
      <p>{t('helpPage.callText')}</p>
      {/* In full, for someone who dials it from another phone. */}
      <p className="help-phone">{formatPhone(CALL_CENTER_PHONE)}</p>
      <a href={`tel:${CALL_CENTER_PHONE}`} className="button button-block button-secondary">
        <PhoneIcon className="button-icon" />
        {t('helpPage.call')}
      </a>
    </div>
  );
}
