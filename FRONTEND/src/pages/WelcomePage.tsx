import { Link } from 'react-router-dom';

/** First screen of a visitor: three large choices, nothing else.
 *  Copied in index.html, shown before the app has loaded: change both together. */
export function WelcomePage() {
  return (
    <section>
      <h1>Bienvenue</h1>
      <p>Des trajets solidaires vers l'emploi, la formation, les soins et les démarches.</p>
      <nav className="stack" aria-label="Accès au compte">
        <Link to="/connexion" className="button button-block">
          Se connecter
        </Link>
        <Link to="/inscription" className="button button-block">
          Créer un compte
        </Link>
        <Link to="/activation" className="button button-block button-secondary">
          J'ai reçu un code
        </Link>
      </nav>
      <p className="note">
        Vous êtes chauffeur ? Votre compte est créé par l'équipe après la vérification de vos documents. Utilisez
        ensuite le code reçu.
      </p>
    </section>
  );
}
