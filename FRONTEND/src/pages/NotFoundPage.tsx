import { Link } from 'react-router-dom';

import { PageHero, PageSheet } from '../components/layout/PageHero';

export function NotFoundPage() {
  return (
    <section>
      <PageHero title="Page introuvable" />
      <PageSheet>
        <Link to="/" className="button">
          Retour à l'accueil
        </Link>
      </PageSheet>
    </section>
  );
}
