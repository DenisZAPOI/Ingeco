import { Link } from 'react-router-dom';

import { PageHero, PageSheet } from '../components/layout/PageHero';
import { t } from '../i18n';

export function NotFoundPage() {
  return (
    <section>
      <PageHero title={t('common.notFound')} />
      <PageSheet>
        <Link to="/" className="button">
          {t('common.backHome')}
        </Link>
      </PageSheet>
    </section>
  );
}
