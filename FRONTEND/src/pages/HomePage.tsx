import { Link } from 'react-router-dom';

import type { Role } from '../api/auth';
import { DriverHome } from '../components/driver/DriverHome';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { HomeIllustration } from '../components/home/HomeIllustration';
import { NeedCards } from '../components/home/NeedCards';
import { NextRide } from '../components/rides/NextRide';
import { ArrowRightIcon, CalendarIcon, UserIcon } from '../components/ui/icons';
import { t } from '../i18n';
import { ADMIN_ACCOUNTS_PATH, PROFILE_PATH, RIDES_PATH } from '../lib/paths';
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
      <PageHero title={t('home.greeting', { name: account.firstName })} art={isRider ? <HomeIllustration /> : undefined}>
        {isRider && <p className="hero-lead">{t('home.riderLead')}</p>}
      </PageHero>
      <PageSheet>
        {account.role === 'rider' ? (
          <>
            <NextRide />
            <NeedCards />
            {/* Below the three needs, smaller: they are not needs but the rider's own pages. */}
            <ul className="quick-links">
              <li>
                <Link to={RIDES_PATH} className="link-action">
                  <CalendarIcon className="button-icon" />
                  {t('home.myRides')}
                </Link>
              </li>
              <li>
                <Link to={PROFILE_PATH} className="link-action">
                  <UserIcon className="button-icon" />
                  {t('home.profile')}
                </Link>
              </li>
            </ul>
          </>
        ) : account.role === 'driver' ? (
          <DriverHome />
        ) : account.role === 'admin' ? (
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
        ) : (
          <>
            <h2>{coming(account.role).title}</h2>
            <p>{coming(account.role).coming}</p>
          </>
        )}
        {!isRider && (
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
