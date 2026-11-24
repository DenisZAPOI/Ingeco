import { Link } from 'react-router-dom';

import { PageHero, PageSheet } from '../components/layout/PageHero';
import { t } from '../i18n';
import { MY_DATA_PATH } from '../lib/paths';

// The sections of the page, in reading order; their texts are privacy.<id>Title and privacy.<id>Text.
const SECTIONS = ['who', 'what', 'never', 'sees', 'howLong', 'rights'] as const;

/** « Vos données » (RGPD art. 13, audit R2): what the application keeps, why,
 *  who sees it, for how long, and the person's rights. Public: read before
 *  creating an account. */
export function PrivacyPage() {
  return (
    <section>
      <PageHero title={t('privacy.title')} />
      <PageSheet>
        <p className="alert alert-info">{t('privacy.lead')}</p>
        {SECTIONS.map((id) => (
          <div key={id}>
            <h2>{t(`privacy.${id}Title`)}</h2>
            <p>{t(`privacy.${id}Text`)}</p>
          </div>
        ))}
        <Link to={MY_DATA_PATH} className="link-action">
          {t('privacy.seeMyData')}
        </Link>
      </PageSheet>
    </section>
  );
}
