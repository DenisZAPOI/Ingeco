import { Link } from 'react-router-dom';

import { t, type TextKey } from '../../i18n';
import { BOOKING_START_PATH, HELP_PATH, JOBS_PATH } from '../../lib/paths';
import { NeedArt } from './NeedArt';

/** A text of the needs (none has a {placeholder}). */
type NeedKey = Extract<TextKey, `needs.${string}`>;

type Need = {
  to: string;
  title: NeedKey;
  hint: NeedKey;
  /** The color and drawing of the need (charter, part 2): they decorate, the title says it. */
  tone: 'work' | 'ride' | 'help';
};

/** The three needs of the home screen, in the order of the cahier des charges (§10). */
const NEEDS: readonly Need[] = [
  { to: JOBS_PATH, title: 'needs.work', hint: 'needs.workHint', tone: 'work' },
  // A visitor is sent to the login page first, then back to the booking.
  { to: BOOKING_START_PATH, title: 'needs.ride', hint: 'needs.rideHint', tone: 'ride' },
  { to: HELP_PATH, title: 'needs.help', hint: 'needs.helpHint', tone: 'help' },
];

/** The home screen organised by needs, not by features (cahier des charges
 *  §10): the three main actions of a visitor and of a rider. */
export function NeedCards() {
  return (
    <nav aria-label={t('needs.label')}>
      <ul className="need-list">
        {NEEDS.map(({ to, title, hint, tone }) => (
          <li key={tone}>
            <Link to={to} className={`action-card need-card need-${tone}`}>
              <span className="action-card-text">
                <span className="action-card-title">{t(title)}</span>
                <span className="action-card-hint">{t(hint)}</span>
              </span>
              <NeedArt tone={tone} />
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
