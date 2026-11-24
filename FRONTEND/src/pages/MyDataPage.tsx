import { Link } from 'react-router-dom';

import { fetchMyData, type HelpRequest, type MyData } from '../api/privacy';
import type { Ride } from '../api/rides';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { RequestState } from '../components/ui/RequestState';
import { useRequest } from '../hooks/useRequest';
import { t, tn } from '../i18n';
import { formatDateTime } from '../lib/format';
import { PRIVACY_PATH, PROFILE_PATH } from '../lib/paths';
import { formatPhone } from '../lib/phone';
import { statusLabel } from '../lib/ride';

const FILE_NAME = 'mes-donnees.json';
const JSON_INDENT = 2;

/** « Mes données » (RGPD art. 15 and 20, audit R3): everything the application
 *  keeps about the person, to read here or to download as a file. */
export function MyDataPage() {
  const data = useRequest(fetchMyData);

  return (
    <section>
      <PageHero title={t('myData.title')} />
      <PageSheet>
        <RequestState loading={data.loading} error={data.error} onRetry={data.retry}>
          {data.data && <MyDataView data={data.data} />}
        </RequestState>
        <Link to={PRIVACY_PATH} className="link-action">
          {t('myData.whyKept')}
        </Link>
        <Link to={PROFILE_PATH} className="link-action">
          {t('myData.backToProfile')}
        </Link>
      </PageSheet>
    </section>
  );
}

function MyDataView({ data }: { data: MyData }) {
  const { account } = data;
  return (
    <>
      <p>{t('myData.lead')}</p>
      <button type="button" className="button button-block" onClick={() => download(data)}>
        {t('myData.download')}
      </button>

      <h2>{t('myData.accountTitle')}</h2>
      <dl className="panel summary">
        <dt>{t('fields.firstName')}</dt>
        <dd>{account.firstName}</dd>
        <dt>{t('fields.lastName')}</dt>
        <dd>{account.lastName}</dd>
        <dt>{t('profile.phone')}</dt>
        <dd>{formatPhone(account.phone)}</dd>
        <dt>{t('fields.emailOptional')}</dt>
        <dd>{account.email ?? t('myData.none')}</dd>
        <dt>{t('myData.createdOn')}</dt>
        <dd>{formatDateTime(account.createdAt)}</dd>
      </dl>

      <h2>{t('myData.ridesTitle')}</h2>
      <p>{tn('myData.rideCount', data.rides.length)}</p>
      {data.rides.length > 0 && (
        <ul>
          {data.rides.map((ride) => (
            <li key={ride.id}>{rideLine(ride)}</li>
          ))}
        </ul>
      )}

      {data.plan && (
        <>
          <h2>{t('myData.planTitle')}</h2>
          <ol>
            {data.plan.steps.map((step) => (
              <li key={step.position}>{t(`orientation.steps.${step.code}.title`)}</li>
            ))}
          </ol>
        </>
      )}

      <h2>{t('myData.helpTitle')}</h2>
      {data.helpRequests.length === 0 ? (
        <p>{t('myData.none')}</p>
      ) : (
        <ul>
          {data.helpRequests.map((request) => (
            <li key={request.createdAt}>{helpLine(request)}</li>
          ))}
        </ul>
      )}

      {data.deletionRequestedAt && (
        <p className="alert alert-info">{t('myData.deletionPending', { date: formatDateTime(data.deletionRequestedAt) })}</p>
      )}
    </>
  );
}

function rideLine(ride: Ride): string {
  const when = formatDateTime(ride.scheduledAt ?? ride.createdAt);
  return t('myData.rideLine', { when, from: ride.pickup.address, to: ride.dropoff.address, status: statusLabel(ride.status) });
}

function helpLine(request: HelpRequest): string {
  const when = formatDateTime(request.createdAt);
  const state = request.handledAt ? t('myData.handled') : t('myData.waiting');
  return t('myData.helpLine', { kind: t(`myData.helpKinds.${request.kind}`), when, state });
}

/** The whole answer of the API, as a file: readable by another service (portability, art. 20). */
function download(data: MyData): void {
  const file = new Blob([JSON.stringify(data, null, JSON_INDENT)], { type: 'application/json' });
  const url = URL.createObjectURL(file);
  const link = document.createElement('a');
  link.href = url;
  link.download = FILE_NAME;
  link.click();
  URL.revokeObjectURL(url);
}
