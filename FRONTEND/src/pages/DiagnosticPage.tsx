import { PageHero, PageSheet } from '../components/layout/PageHero';
import { RequestState } from '../components/ui/RequestState';
import { useHealth } from '../hooks/useHealth';
import { t } from '../i18n';

/** Checks the chain front → API → database. */
export function DiagnosticPage() {
  const { health, loading, error, retry } = useHealth();

  return (
    <section>
      <PageHero title={t('diagnostic.title')} />
      <PageSheet>
        <RequestState loading={loading} error={error} onRetry={retry}>
          {health && (
            <ul className="panel">
              <li>
                {t('diagnostic.api', {
                  state: health.status === 'ok' ? t('diagnostic.apiOk') : t('diagnostic.apiDegraded'),
                })}
              </li>
              <li>
                {t('diagnostic.database', {
                  state: health.database.reachable
                    ? t('diagnostic.databaseOk', { dialect: health.database.dialect ?? '' })
                    : t('diagnostic.databaseDown'),
                })}
              </li>
            </ul>
          )}
        </RequestState>
      </PageSheet>
    </section>
  );
}
