import { Link } from 'react-router-dom';

import type { Role } from '../api/auth';
import { CarIcon } from '../components/ui/icons';
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
      <h1>Bonjour {account.firstName}</h1>
      {account.role === 'rider' ? (
        <div className="stack">
          <Link to="/reserver" className="button button-block">
            <CarIcon className="button-icon" />
            Réserver un trajet
          </Link>
          <Link to="/profil" className="button button-block button-secondary">
            Mon profil
          </Link>
        </div>
      ) : (
        <>
          <h2>{COMING[account.role].title}</h2>
          <p>{COMING[account.role].coming}</p>
          <Link to="/profil" className="button button-block button-secondary">
            Mon profil
          </Link>
        </>
      )}
    </section>
  );
}
