import type { ComponentType } from 'react';
import { NavLink } from 'react-router-dom';

import type { Role } from '../../api/auth';
import { t, type TextKey } from '../../i18n';
import { DRIVER_RIDES_PATH, EARNINGS_PATH, ORIENTATION_PLAN_PATH, PROFILE_PATH, RIDES_PATH } from '../../lib/paths';
import { CalendarIcon, CarIcon, HouseIcon, PlanIcon, TicketIcon, UserIcon } from '../ui/icons';

/** A word of the navigation (none has a {placeholder}). */
type NavKey = Extract<TextKey, `nav.${string}`>;

type NavEntry = {
  to: string;
  Icon: ComponentType<{ className?: string }>;
  label: NavKey;
};

const HOME: NavEntry = { to: '/', Icon: HouseIcon, label: 'nav.home' };
const PROFILE: NavEntry = { to: PROFILE_PATH, Icon: UserIcon, label: 'nav.profile' };

const RIDER_ENTRIES: readonly NavEntry[] = [
  HOME,
  { to: RIDES_PATH, Icon: CalendarIcon, label: 'nav.rides' },
  { to: ORIENTATION_PLAN_PATH, Icon: PlanIcon, label: 'nav.plan' },
  PROFILE,
];

const DRIVER_ENTRIES: readonly NavEntry[] = [
  HOME,
  { to: DRIVER_RIDES_PATH, Icon: CarIcon, label: 'nav.driverRides' },
  { to: EARNINGS_PATH, Icon: TicketIcon, label: 'nav.earnings' },
  PROFILE,
];

export type NavRole = 'rider' | 'driver';

/** The roles that move between their own pages every day. The others
 *  (visitor, administrator, operator, partner) keep the home screen only. */
export function navRole(role: Role | undefined): NavRole | null {
  if (role === 'rider' || role === 'driver') return role;
  return null;
}

/** The pages of a rider or a driver: a bar at the bottom of a phone, a column
 *  on the left of a large screen (the CSS decides). Not the main actions of a
 *  screen: those stay in the page. */
export function AppNav({ role }: { role: NavRole }) {
  const entries = role === 'rider' ? RIDER_ENTRIES : DRIVER_ENTRIES;
  return (
    <nav className="app-nav" aria-label={t('nav.label')}>
      <ul className="app-nav-list">
        {entries.map(({ to, Icon, label }) => (
          <li key={to}>
            {/* "end" on the home only: "/" would otherwise be current everywhere. */}
            <NavLink to={to} end={to === HOME.to} className="app-nav-link">
              <span className="app-nav-icon">
                <Icon />
              </span>
              {t(label)}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
