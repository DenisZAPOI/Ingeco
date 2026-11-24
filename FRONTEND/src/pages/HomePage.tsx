import { Link } from 'react-router-dom';

import type { Role } from '../api/auth';
import { DriverHome } from '../components/driver/DriverHome';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { NeedCards } from '../components/home/NeedCards';
import { PlanLink } from '../components/orientation/PlanLink';
import { NextRide } from '../components/rides/NextRide';
import { ArrowRightIcon, ClockIcon, PhoneIcon, UserIcon } from '../components/ui/icons';
import { t } from '../i18n';
import { ADMIN_ACCOUNTS_PATH, ADMIN_SETTINGS_PATH, PROFILE_PATH, STAFF_REQUESTS_PATH } from '../lib/paths';
import { useSession } from '../hooks/useSession';
import { WelcomePage } from './WelcomePage';

// Temporary home of the roles whose screens do not exist yet (steps 3 to 7).
function coming(role: Exclude<Role, 'rider' | 'driver' | 'admin'>): { title: string; coming: string } {
  return role === 'partner'
    ? { title: t('home.partnerTitle'), coming: t('home.partnerComing') }
    : { title: t('home.operatorTitle'), coming: t('home.operatorComing') };
}

/** Visitor: the welcome screen. Logged in: the home of their role, drawn from
 *  the last session's hint until the API confirms it. */
export function HomePage() {
  const { user, hint } = useSession();
  const account = user ?? hint;
  if (!account) {
    return <WelcomePage />;
  }

  const isRider = account.role === 'rider';
  return (
    <section>
      <PageHero title={t('home.greeting', { name: account.firstName })}>
        {isRider && <p className="hero-lead">{t('home.riderLead')}</p>}
      </PageHero>
      <PageSheet>
        {account.role === 'rider' ? (
          <>
            <NextRide />
            <NeedCards />
            {/* Below the three needs, smaller: where the plan stands. The rider's
                own pages (trips, plan, profile) are in the navigation. */}
            <ul className="quick-links">
              <PlanLink />
            </ul>
          </>
        ) : account.role === 'driver' ? (
          <DriverHome />
        ) : account.role === 'admin' ? (
          <div className="stack">
            <Link to={ADMIN_ACCOUNTS_PATH} className="action-card action-card-primary">
              <span className="icon-chip icon-chip-sun">
                <UserIcon />
              </span>
              <span className="action-card-text">
                <span className="action-card-title">{t('home.accounts')}</span>
                <span className="action-card-hint">{t('home.accountsHint')}</span>
              </span>
              <ArrowRightIcon className="action-card-arrow" />
            </Link>
            <Link to={ADMIN_SETTINGS_PATH} className="action-card">
              <span className="icon-chip">
                <ClockIcon />
              </span>
              <span className="action-card-text">
                <span className="action-card-title">{t('home.settings')}</span>
                <span className="action-card-hint">{t('home.settingsHint')}</span>
              </span>
              <ArrowRightIcon className="action-card-arrow" />
            </Link>
            <RequestsCard />
          </div>
        ) : account.role === 'operator' ? (
          <div className="stack">
            <p>{t('home.operatorComing')}</p>
            <RequestsCard />
          </div>
        ) : (
          <>
            <h2>{coming(account.role).title}</h2>
            <p>{coming(account.role).coming}</p>
          </>
        )}
        {/* A driver reaches their profile from the navigation. */}
        {!isRider && account.role !== 'driver' && (
          <div className="stack">
            <Link to={PROFILE_PATH} className="action-card">
              <span className="icon-chip">
                <UserIcon />
              </span>
              <span className="action-card-title">{t('home.profile')}</span>
              <ArrowRightIcon className="action-card-arrow" />
            </Link>
          </div>
        )}
      </PageSheet>
    </section>
  );
}

/** Operator and administrator: the callbacks to make (and, for the administrator, the accounts to delete). */
function RequestsCard() {
  return (
    <Link to={STAFF_REQUESTS_PATH} className="action-card">
      <span className="icon-chip">
        <PhoneIcon />
      </span>
      <span className="action-card-text">
        <span className="action-card-title">{t('home.requests')}</span>
        <span className="action-card-hint">{t('home.requestsHint')}</span>
      </span>
      <ArrowRightIcon className="action-card-arrow" />
    </Link>
  );
}
