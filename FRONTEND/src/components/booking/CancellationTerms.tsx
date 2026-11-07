import { t } from '../../i18n';

/** What happens if the trip is cancelled, shown before the booking is sent
 *  (cahier des charges §7.4). The rules are those of the API: see
 *  CANCELLABLE_STATUSES in services/ride_rules.py and docs/decisions.md (Q7). */
export function CancellationTerms() {
  return (
    <section className="panel" aria-labelledby="cancellation-terms">
      <h2 id="cancellation-terms" className="panel-title">
        {t('booking.cancelTitle')}
      </h2>
      <ul className="panel-list">
        <li>{t('booking.cancelFree')}</li>
        <li>{t('booking.cancelRefund')}</li>
        <li>{t('booking.cancelDriver')}</li>
      </ul>
    </section>
  );
}
