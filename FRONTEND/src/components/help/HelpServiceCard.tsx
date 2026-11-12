import { Link } from 'react-router-dom';

import type { HelpService } from '../../api/helpServices';
import { t } from '../../i18n';
import { languageLabel, speaksAppLanguage } from '../../lib/helpServices';
import { helpServicePath } from '../../lib/paths';
import { ArrowRightIcon } from '../ui/icons';

/** A service in the list: its name, where and when, and what matters to
 *  decide to go. Opens its page without a new wait. */
export function HelpServiceCard({ service }: { service: HelpService }) {
  return (
    <Link to={helpServicePath(service.id)} state={{ service }} className="ride-card">
      <span className="ride-card-text">
        {/* The language of the service's own texts: French when it is not translated. */}
        <span className="ride-card-when" lang={service.language}>
          {service.name}
        </span>
        <span className="ride-card-to">{service.communeName}</span>
        <span className="ride-card-to" lang={service.language}>
          {service.hours}
        </span>
        <HelpServiceBadges service={service} />
      </span>
      <ArrowRightIcon className="action-card-arrow" />
    </Link>
  );
}

/** "Accessible en fauteuil roulant", "Parle créole guyanais": in words, never by a colour alone. */
export function HelpServiceBadges({ service }: { service: HelpService }) {
  const spoken = speaksAppLanguage(service);
  if (!service.wheelchairAccessible && !spoken) return null;
  return (
    <span className="badges">
      {service.wheelchairAccessible && <span className="badge">{t('helpServices.accessible')}</span>}
      {spoken && <span className="badge">{t('helpServices.speaks', { language: languageLabel(spoken) })}</span>}
    </span>
  );
}

export function HelpServiceList({ services }: { services: HelpService[] }) {
  return (
    <ul className="ride-list">
      {services.map((service) => (
        <li key={service.id}>
          <HelpServiceCard service={service} />
        </li>
      ))}
    </ul>
  );
}
