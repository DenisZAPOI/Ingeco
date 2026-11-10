import { Link } from 'react-router-dom';

import type { JobOffer } from '../../api/jobs';
import { t } from '../../i18n';
import { scheduleLabel } from '../../lib/jobs';
import { jobPath } from '../../lib/paths';
import { ArrowRightIcon } from '../ui/icons';

/** An offer in the list: what, where, when, and the two badges that matter
 *  most to a beginner. Opens its page without a new wait. */
export function JobCard({ offer }: { offer: JobOffer }) {
  return (
    <Link to={jobPath(offer.id)} state={{ offer }} className="ride-card">
      <span className="ride-card-text">
        {/* The language of the offer's own texts: French when it is not
            translated, read with the right voice by a screen reader. */}
        <span className="ride-card-when" lang={offer.language}>
          {offer.title}
        </span>
        <span lang={offer.language}>{offer.employer}</span>
        <span className="ride-card-to">
          {offer.communeName} · {scheduleLabel(offer.schedule)}
        </span>
        <JobBadges offer={offer} />
      </span>
      <ArrowRightIcon className="action-card-arrow" />
    </Link>
  );
}

/** "Débutant accepté", "Sans diplôme": in words, never by a colour alone. */
export function JobBadges({ offer }: { offer: JobOffer }) {
  if (!offer.beginnerWelcome && !offer.noDiplomaRequired) return null;
  return (
    <span className="badges">
      {offer.beginnerWelcome && <span className="badge">{t('jobs.beginnerWelcome')}</span>}
      {offer.noDiplomaRequired && <span className="badge">{t('jobs.noDiplomaRequired')}</span>}
    </span>
  );
}

export function JobList({ offers }: { offers: JobOffer[] }) {
  return (
    <ul className="ride-list">
      {offers.map((offer) => (
        <li key={offer.id}>
          <JobCard offer={offer} />
        </li>
      ))}
    </ul>
  );
}
