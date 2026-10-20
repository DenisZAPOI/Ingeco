import { Link } from 'react-router-dom';

import type { Role } from '../api/auth';
import { useSession } from '../hooks/useSession';
import { WelcomePage } from './WelcomePage';

// Temporary home of each role, until its real screens exist (steps 3 to 7).
const SPACES: Record<Role, { title: string; coming: string }> = {
  rider: { title: 'Mes trajets', coming: 'Vous pourrez bientôt réserver un trajet ici.' },
  driver: { title: 'Espace chauffeur', coming: 'Vous pourrez bientôt recevoir et accepter des courses ici.' },
  partner: { title: 'Espace partenaire', coming: 'Vous pourrez bientôt émettre des bons solidaires ici.' },
  operator: { title: "Centre d'appel", coming: 'Vous pourrez bientôt réserver pour un usager ici.' },
  admin: { title: 'Administration', coming: 'Vous pourrez bientôt gérer les comptes ici.' },
};

/** Visitor: the welcome screen. Logged in: the home of their role. */
export function HomePage() {
  const { user } = useSession();
  if (!user) {
    return <WelcomePage />;
  }

  const space = SPACES[user.role];
  return (
    <section>
      <h1>Bonjour {user.firstName}</h1>
      <h2>{space.title}</h2>
      <p>{space.coming}</p>
      <Link to="/profil" className="button button-block button-secondary">
        Mon profil
      </Link>
    </section>
  );
}
