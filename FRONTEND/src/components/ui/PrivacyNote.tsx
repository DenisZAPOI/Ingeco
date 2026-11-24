import { Link } from 'react-router-dom';

import { t } from '../../i18n';
import { PRIVACY_PATH } from '../../lib/paths';

/** Where personal data is asked (RGPD art. 13, audit R2): what is kept and why. */
export function PrivacyNote() {
  return (
    <p className="note">
      <Link to={PRIVACY_PATH}>{t('common.privacyNote')}</Link>
    </p>
  );
}
