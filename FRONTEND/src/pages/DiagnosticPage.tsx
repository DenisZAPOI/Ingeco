import { PageHero, PageSheet } from '../components/layout/PageHero';
import { RequestState } from '../components/ui/RequestState';
import { useHealth } from '../hooks/useHealth';

/** Checks the chain front → API → database. */
export function DiagnosticPage() {
  const { health, loading, error, retry } = useHealth();

  return (
    <section>
      <PageHero title="État du service" />
      <PageSheet>
        <RequestState loading={loading} error={error} onRetry={retry}>
          {health && (
            <ul className="panel">
              <li>API : {health.status === 'ok' ? 'en ligne' : 'dégradée'}</li>
              <li>
                Base de données : {health.database.reachable ? `joignable (${health.database.dialect})` : 'injoignable'}
              </li>
            </ul>
          )}
        </RequestState>
      </PageSheet>
    </section>
  );
}
