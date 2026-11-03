import { PageHero, PageSheet } from '../components/layout/PageHero';
import { CLIENT_FALLBACK, CLIENT_NAME, DATABASE_TEAM, DEVELOPERS, OSM_COPYRIGHT_URL } from '../lib/about';

/** What the app is (a student demonstrator, nothing real) and who made it.
 *  Public: linked from the footer of every screen. */
export function AboutPage() {
  return (
    <section>
      <PageHero title="À propos" />
      <PageSheet>
        <h2>Un projet étudiant</h2>
        <p>
          Cette application est un démonstrateur : elle montre comment un service de trajets solidaires pourrait
          marcher en Guyane. Ce n'est pas encore un vrai service.
        </p>
        <ul>
          <li>Les comptes et les trajets sont des exemples.</li>
          <li>Aucun paiement n'est réel : le paiement est simulé.</li>
          <li>Aucun SMS n'est envoyé : ils sont simulés.</li>
          <li>Aucun chauffeur ne viendra vous chercher.</li>
        </ul>

        <h2>Qui l'a réalisé</h2>
        <p>
          Des étudiants en BUT 3 Informatique à l'IUT de Montreuil, pour {CLIENT_NAME ?? CLIENT_FALLBACK}.
        </p>
        <dl className="credits">
          <dt>Développement</dt>
          <dd>{DEVELOPERS.join(', ')}</dd>
          <dt>Base de données</dt>
          <dd>{DATABASE_TEAM.join(', ')}</dd>
        </dl>

        <h2>Cartes et adresses</h2>
        <p>
          Adresses et distances calculées avec OpenRouteService, à partir des données ©{' '}
          <a href={OSM_COPYRIGHT_URL} target="_blank" rel="noopener noreferrer">
            contributeurs d'OpenStreetMap
          </a>
          .
        </p>
      </PageSheet>
    </section>
  );
}
