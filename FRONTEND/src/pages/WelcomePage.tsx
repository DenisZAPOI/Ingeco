import { Link } from 'react-router-dom';

import { CarIcon, LogoMark, PhoneIcon, TicketIcon, WheelchairIcon } from '../components/ui/icons';
import { formatPhone } from '../lib/phone';

// Given by the client, in international format (+594…). Until then the help
// block stays hidden: a wrong number would be worse than none.
const CALL_CENTER_PHONE: string | null = import.meta.env.VITE_CALL_CENTER_PHONE || null;

const BENEFITS = [
  { Icon: CarIcon, text: 'Un chauffeur vient vous chercher et vous dépose.' },
  { Icon: TicketIcon, text: 'Une association, une mairie ou un employeur peut payer tout ou partie du trajet.' },
  { Icon: WheelchairIcon, text: 'Un véhicule adapté au fauteuil roulant, sur demande.' },
];

/** First screen of a visitor: what the service is, then one main choice.
 *  Copied in index.html, shown before the app has loaded: change both together. */
export function WelcomePage() {
  return (
    <section>
      <div className="welcome-hero">
        <LogoMark className="welcome-logo" />
        <h1>Bienvenue</h1>
        <p className="lead">Des trajets solidaires pour aller au travail, en formation, aux soins et aux démarches.</p>
      </div>

      <ul className="benefits">
        {BENEFITS.map(({ Icon, text }) => (
          <li key={text} className="benefit">
            <span className="benefit-icon">
              <Icon />
            </span>
            {text}
          </li>
        ))}
      </ul>

      <nav className="stack" aria-label="Accès au compte">
        <Link to="/inscription" className="button button-block">
          Créer un compte
        </Link>
        <Link to="/connexion" className="button button-block button-secondary">
          J'ai déjà un compte
        </Link>
      </nav>

      <p className="note">
        Compte créé par le centre d'appel, ou vous êtes chauffeur ?{' '}
        <Link to="/activation" className="link-action">
          J'ai reçu un code
        </Link>
      </p>

      {CALL_CENTER_PHONE && (
        <div className="panel help">
          <h2>Besoin d'aide ?</h2>
          <p>Le centre d'appel peut créer votre compte et réserver vos trajets avec vous.</p>
          {/* In full, for someone who dials it from another phone. */}
          <p className="help-phone">{formatPhone(CALL_CENTER_PHONE)}</p>
          <a href={`tel:${CALL_CENTER_PHONE}`} className="button button-block button-secondary">
            <PhoneIcon className="button-icon" />
            Appeler
          </a>
        </div>
      )}
    </section>
  );
}
