import { Link } from 'react-router-dom';

import type { Role } from '../api/auth';
import { DriverHome } from '../components/driver/DriverHome';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { NextRide } from '../components/rides/NextRide';
import { ArrowRightIcon, CalendarIcon, CarIcon, UserIcon } from '../components/ui/icons';
import { RIDES_PATH } from '../lib/paths';
import { useSession } from '../hooks/useSession';
import { WelcomePage } from './WelcomePage';

// Temporary home of the roles whose screens do not exist yet (steps 3 to 7).
const COMING: Record<Exclude<Role, 'rider' | 'driver'>, { title: string; coming: string }> = {
  partner: { title: 'Espace partenaire', coming: 'Vous pourrez bientôt émettre des bons solidaires ici.' },
  operator: { title: "Centre d'appel", coming: 'Vous pourrez bientôt réserver pour un usager ici.' },
  admin: { title: 'Administration', coming: 'Vous pourrez bientôt gérer les comptes ici.' },
};

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
      <PageHero title={`Bonjour ${account.firstName}`}>
        {account.role === 'rider' && <p className="hero-lead">Où allez-vous aujourd'hui ?</p>}
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
                <span className="action-card-title">Réserver un trajet</span>
                <span className="action-card-hint">Emploi, formation, soins, démarches</span>
              </span>
              <ArrowRightIcon className="action-card-arrow" />
            </Link>
          </>
        ) : account.role === 'driver' ? (
          <DriverHome />
        ) : (
          <>
            <h2>{COMING[account.role].title}</h2>
            <p>{COMING[account.role].coming}</p>
          </>
        )}
        <div className="stack">
          {account.role === 'rider' && (
            <Link to={RIDES_PATH} className="action-card">
              <span className="icon-chip">
                <CalendarIcon />
              </span>
              <span className="action-card-text">
                <span className="action-card-title">Mes trajets</span>
                <span className="action-card-hint">À venir et passés</span>
              </span>
              <ArrowRightIcon className="action-card-arrow" />
            </Link>
          )}
          <Link to="/profil" className="action-card">
            <span className="icon-chip">
              <UserIcon />
            </span>
            <span className="action-card-title">Mon profil</span>
            <ArrowRightIcon className="action-card-arrow" />
          </Link>
        </div>
      </PageSheet>
    </section>
  );
}
