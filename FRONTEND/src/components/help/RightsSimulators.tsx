import { t } from '../../i18n';
import { RIGHTS_SIMULATORS } from '../../lib/helpServices';

/** Official simulators of benefits (cahier des charges §7.5), with the "rights"
 *  services. Same tab, like the training catalogues: the phone's Back button
 *  returns to the app. */
export function RightsSimulators() {
  return (
    <div className="panel">
      <h2 className="panel-title">{t('helpServices.simulators.title')}</h2>
      <p>{t('helpServices.simulators.lead')}</p>
      <div className="stack">
        {RIGHTS_SIMULATORS.map(({ id, url }) => (
          <div key={id}>
            <p>{t(`helpServices.simulators.${id}.description`)}</p>
            {/* The text names the site: the user knows they leave the app. */}
            <a href={url} className="button button-block button-secondary" rel="noopener noreferrer">
              {t(`helpServices.simulators.${id}.open`)}
            </a>
          </div>
        ))}
      </div>
      <p className="note">{t('helpServices.simulators.outside')}</p>
    </div>
  );
}
