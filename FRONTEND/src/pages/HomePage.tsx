import { Link } from 'react-router-dom';

import type { Role } from '../api/auth';
import { DriverHome } from '../components/driver/DriverHome';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { NextRide } from '../components/rides/NextRide';
import { ArrowRightIcon, CalendarIcon, CarIcon, UserIcon } from '../components/ui/icons';
import { t } from '../i18n';
import { ADMIN_ACCOUNTS_PATH, RIDES_PATH } from '../lib/paths';
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

  return (
    <section>
      <PageHero title={t('home.greeting', { name: account.firstName })}>
        {account.role === 'rider' && <p className="hero-lead">{t('home.riderLead')}</p>}
      </PageHero>
      <PageSheet>
        {account.role === 'rider' ? (
          <>
            <NextRide />
            <Link to="/reserver" className="action-card action-card-primary">
              <span className="icon-chip icon-chip-sun">
                <CarIcon />
              </span>
              <span className="action-card-text">
                <span className="action-card-title">{t('home.book')}</span>
                <span className="action-card-hint">{t('home.bookHint')}</span>
              </span>
              <ArrowRightIcon className="action-card-arrow" />
            </Link>
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
        <div className="stack">
          {account.role === 'rider' && (
            <Link to={RIDES_PATH} className="action-card">
              <span className="icon-chip">
                <CalendarIcon />
              </span>
              <span className="action-card-text">
                <span className="action-card-title">{t('home.myRides')}</span>
                <span className="action-card-hint">{t('home.myRidesHint')}</span>
              </span>
              <ArrowRightIcon className="action-card-arrow" />
            </Link>
          )}
          <Link to="/profil" className="action-card">
            <span className="icon-chip">
              <UserIcon />
            </span>
            <span className="action-card-title">{t('home.profile')}</span>
            <ArrowRightIcon className="action-card-arrow" />
          </Link>
        </div>
      </PageSheet>
    </section>
  );
}
