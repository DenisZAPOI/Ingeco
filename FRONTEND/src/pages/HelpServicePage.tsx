import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';

import type { HelpService } from '../api/helpServices';
import { HelpServiceBadges } from '../components/help/HelpServiceCard';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { PhoneIcon } from '../components/ui/icons';
import { RequestState } from '../components/ui/RequestState';
import { useHelpService } from '../hooks/useHelpServices';
import { t } from '../i18n';
import { draftForHelpService, saveBookingDraft } from '../lib/bookingDraft';
import { categoryLabel, filtersToParams, formatUpdatedOn, languageLabel, purposeFor, serviceFromState } from '../lib/helpServices';
import { BOOKING_PATHS, HELP_SERVICES_PATH } from '../lib/paths';
import { formatPhone } from '../lib/phone';

/** One help service, and its main action: "Comment y aller ?". */
export function HelpServicePage() {
  const id = Number(useParams().id);
  const location = useLocation();
  const navigate = useNavigate();
  const handed = serviceFromState(location.state, id);
  const service = useHelpService(id, handed);
  const category = service.data?.category;

  return (
    <section>
      <PageHero title={service.data?.name ?? t('helpServices.serviceTitle')} lang={service.data?.language}>
        {category && <p className="hero-lead">{categoryLabel(category)}</p>}
      </PageHero>
      <PageSheet>
        {/* A service already shown stays shown if the confirmation fails (slow network). */}
        <RequestState loading={service.loading && !service.data} error={service.data ? null : service.error} onRetry={service.retry}>
          {service.data && <ServiceDetail service={service.data} />}
        </RequestState>
        {/* Opened from the list: back to it as it was left (its commune is in
            its address). Opened from a link: to the services of this need. */}
        <Link
          to={category ? `${HELP_SERVICES_PATH}?${new URLSearchParams(filtersToParams({ category, communeId: null }))}` : HELP_SERVICES_PATH}
          onClick={(event) => {
            if (handed) {
              event.preventDefault();
              navigate(-1);
            }
          }}
          className="link-action"
        >
          {t('helpServices.backToList')}
        </Link>
      </PageSheet>
    </section>
  );
}

function ServiceDetail({ service }: { service: HelpService }) {
  const navigate = useNavigate();

  // The booking starts with the service's place and its purpose: only the
  // pickup and the time are left. A visitor is sent to log in first.
  function goThere() {
    saveBookingDraft(draftForHelpService(service.id, service.place, purposeFor(service.category)));
    navigate(BOOKING_PATHS.pickup);
  }

  return (
    <>
      <HelpServiceBadges service={service} />
      <p lang={service.language}>{service.description}</p>
      <dl className="summary">
        <dt>{t('helpServices.address')}</dt>
        <dd>
          {service.place.address} ({service.communeName})
        </dd>
        <dt>{t('helpServices.hours')}</dt>
        <dd lang={service.language}>{service.hours}</dd>
        <dt>{t('helpServices.languages')}</dt>
        <dd>{service.spokenLanguages.map(languageLabel).join(', ')}</dd>
        <dt>{t('helpServices.accessibility')}</dt>
        <dd>{service.wheelchairAccessible ? t('helpServices.accessible') : t('helpServices.notAccessible')}</dd>
        <dt>{t('helpServices.updatedOn')}</dt>
        <dd>{formatUpdatedOn(service.updatedOn)}</dd>
      </dl>
      <button type="button" className="button button-block" onClick={goThere}>
        {t('jobs.howToGetThere')}
      </button>
      <p className="note">{t('jobs.howToGetThereHint')}</p>
      <div className="panel help">
        <h2>{t('helpServices.callTitle')}</h2>
        {/* In full, for someone who dials it from another phone. */}
        <p className="help-phone">{formatPhone(service.phone)}</p>
        <a href={`tel:${service.phone}`} className="button button-block button-secondary">
          <PhoneIcon className="button-icon" />
          {t('helpServices.call')}
        </a>
        <p className="note">{t('helpServices.fictionalPhone')}</p>
      </div>
    </>
  );
}
