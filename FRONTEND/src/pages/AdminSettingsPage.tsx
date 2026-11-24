import { ServiceHoursForm } from '../components/admin/ServiceHoursForm';
import { TariffForm } from '../components/admin/TariffForm';
import { ZonesForm } from '../components/admin/ZonesForm';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { t } from '../i18n';

/** The administrator's settings (§5 M9, P1): hours, served communes, tariff.
 *  One page, each setting saved by its own button (decided on 24/11/2026). */
export function AdminSettingsPage() {
  return (
    <section>
      <PageHero title={t('settings.title')} />
      <PageSheet>
        <p className="alert alert-info">{t('settings.lead')}</p>
        <ServiceHoursForm />
        <ZonesForm />
        <TariffForm />
      </PageSheet>
    </section>
  );
}
