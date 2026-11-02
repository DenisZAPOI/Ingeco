import { useSearchParams } from 'react-router-dom';

import { PageHero, PageSheet } from '../components/layout/PageHero';
import { RequestState } from '../components/ui/RequestState';
import { useEarnings } from '../hooks/useDriver';
import { PERIOD_LABELS, formatEarningsDay, formatRideCount, type EarningsPeriod } from '../lib/earnings';
import { formatPrice } from '../lib/format';

// In the address: the Back button returns to the period the driver was on.
const PERIOD_PARAM = 'periode';
const PERIODS: { key: string; period: EarningsPeriod }[] = [
  { key: 'jour', period: 'today' },
  { key: 'semaine', period: 'week' },
  { key: 'mois', period: 'month' },
];

/** UC28: what the driver earned today, this week or this month, day by day.
 *  The whole price of each completed ride, without commission. */
export function DriverEarningsPage() {
  const [params, setParams] = useSearchParams();
  const period = PERIODS.find((entry) => entry.key === params.get(PERIOD_PARAM))?.period ?? 'today';

  return (
    <section>
      <PageHero title="Mes revenus" />
      <PageSheet>
        <div className="tabs" role="tablist" aria-label="Période">
          {PERIODS.map((entry) => (
            <button
              key={entry.key}
              type="button"
              role="tab"
              className="tab"
              aria-selected={period === entry.period}
              onClick={() => setParams({ [PERIOD_PARAM]: entry.key }, { replace: true })}
            >
              {PERIOD_LABELS[entry.period]}
            </button>
          ))}
        </div>
        <div role="tabpanel">
          {/* key: each period loads its own figures. */}
          <PeriodEarnings key={period} period={period} />
        </div>
      </PageSheet>
    </section>
  );
}

function PeriodEarnings({ period }: { period: EarningsPeriod }) {
  const earnings = useEarnings(period);
  const data = earnings.data;

  return (
    <RequestState loading={earnings.loading} error={earnings.error} onRetry={earnings.retry}>
      {data && (
        <>
          <dl className="panel summary">
            <dt>Total</dt>
            <dd className="summary-price">{formatPrice(data.totalCents)}</dd>
            <dt>Courses terminées</dt>
            <dd>{data.rideCount}</dd>
          </dl>
          {data.days.length === 0 ? (
            <p>Aucune course terminée sur cette période.</p>
          ) : (
            <ul className="earnings-days">
              {data.days.map((day) => (
                <li key={day.day} className="earnings-day">
                  <span>
                    <span className="earnings-day-date">{formatEarningsDay(day.day)}</span>
                    <span className="note">{formatRideCount(day.rideCount)}</span>
                  </span>
                  <strong>{formatPrice(day.totalCents)}</strong>
                </li>
              ))}
            </ul>
          )}
          <p className="note">Le prix entier de chaque course terminée, le jour où elle s'est terminée.</p>
        </>
      )}
    </RequestState>
  );
}
