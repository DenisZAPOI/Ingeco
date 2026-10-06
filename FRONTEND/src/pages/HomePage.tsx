import { Link } from 'react-router-dom';

export function HomePage() {
  return (
    <section>
      <h1>Bienvenue</h1>
      <p>Des trajets solidaires vers l'emploi, la formation, les soins et les démarches.</p>
      <Link to="/diagnostic" className="button">
        Vérifier le service
      </Link>
    </section>
  );
}
