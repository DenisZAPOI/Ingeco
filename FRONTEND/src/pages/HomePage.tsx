import { Link } from 'react-router-dom';

import type { Role } from '../api/auth';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { ArrowRightIcon, CarIcon, UserIcon } from '../components/ui/icons';
import { useSession } from '../hooks/useSession';
import { WelcomePage } from './WelcomePage';

// Temporary home of the roles whose screens do not exist yet (steps 3 to 7).
const COMING: Record<Exclude<Role, 'rider'>, { title: string; coming: string }> = {
  driver: { title: 'Espace chauffeur', coming: 'Vous pourrez bientôt recevoir et accepter des courses ici.' },
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
        ) : (
          <>
            <h2>{COMING[account.role].title}</h2>
            <p>{COMING[account.role].coming}</p>
          </>
        )}
        <div className="stack">
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
