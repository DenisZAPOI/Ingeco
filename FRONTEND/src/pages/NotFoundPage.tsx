import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <section>
      <h1>Page introuvable</h1>
      <Link to="/" className="button">
        Retour à l'accueil
      </Link>
    </section>
  );
}
