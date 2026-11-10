import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';

import type { JobOffer } from '../api/jobs';
import { JobBadges } from '../components/jobs/JobCard';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { RequestState } from '../components/ui/RequestState';
import { useJobOffer } from '../hooks/useJobOffers';
import { t } from '../i18n';
import { draftForJobOffer, saveBookingDraft } from '../lib/bookingDraft';
import { contractLabel, offerFromState, scheduleLabel } from '../lib/jobs';
import { BOOKING_PATHS, JOBS_PATH } from '../lib/paths';

/** One job offer, and its main action: "Comment y aller ?". */
export function JobPage() {
  const id = Number(useParams().id);
  const location = useLocation();
  const navigate = useNavigate();
  const handed = offerFromState(location.state, id);
  const offer = useJobOffer(id, handed);

  return (
    <section>
      <PageHero title={offer.data?.title ?? t('jobs.offerTitle')} lang={offer.data?.language}>
        {offer.data && (
          <p className="hero-lead" lang={offer.data.language}>
            {offer.data.employer}
          </p>
        )}
      </PageHero>
      <PageSheet>
        {/* An offer already shown stays shown if the confirmation fails (slow network). */}
        <RequestState loading={offer.loading && !offer.data} error={offer.data ? null : offer.error} onRetry={offer.retry}>
          {offer.data && <OfferDetail offer={offer.data} />}
        </RequestState>
        {/* Opened from the list: back to it as it was left (its filters are
            in its address). Opened from a link: to the whole list. */}
        <Link
          to={JOBS_PATH}
          onClick={(event) => {
            if (handed) {
              event.preventDefault();
              navigate(-1);
            }
          }}
          className="link-action"
        >
          {t('jobs.backToList')}
        </Link>
      </PageSheet>
    </section>
  );
}

function OfferDetail({ offer }: { offer: JobOffer }) {
  const navigate = useNavigate();

  // The booking starts with the job's place and "Emploi": only the pickup and
  // the time are left. A visitor is sent to log in first, and comes back here.
  function goThere() {
    saveBookingDraft(draftForJobOffer(offer.id, offer.place));
    navigate(BOOKING_PATHS.pickup);
  }

  return (
    <>
      <JobBadges offer={offer} />
      <dl className="summary">
        <dt>{t('jobs.place')}</dt>
        <dd>{offer.place.address}</dd>
        <dt>{t('jobs.contractLabel')}</dt>
        <dd>
          {contractLabel(offer.contractType)}
          {offer.partTime && ` · ${t('jobs.partTime')}`}
        </dd>
        <dt>{t('jobs.scheduleLabel')}</dt>
        <dd>{scheduleLabel(offer.schedule)}</dd>
      </dl>
      <p lang={offer.language}>{offer.description}</p>
      <button type="button" className="button button-block" onClick={goThere}>
        {t('jobs.howToGetThere')}
      </button>
      <p className="note">{t('jobs.howToGetThereHint')}</p>
    </>
  );
}
