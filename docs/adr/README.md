# Fiches de décision d'architecture (ADR)

Le cahier des charges v1.0 (§11) laisse la stack libre, à condition que chaque choix soit
« justifié par une fiche de décision d'architecture ». Une fiche par choix technique : ce qui a
été décidé, pourquoi, ce qui a été écarté, et ce que ça entraîne.

## Règles

- **Une fiche par décision**, une page au plus, numérotée dans l'ordre : `NNN-titre-court.md`.
- **On ne réécrit pas une fiche acceptée.** Si la décision change, on écrit une nouvelle fiche,
  et l'ancienne passe à « Remplacée par NNN ». Une fiche « Proposée » peut encore changer.
- **Statuts** : Proposée (pas encore appliquée), Acceptée, Remplacée par NNN, Abandonnée.
- **Dates** : la date où le choix a été fait. Les fiches 001 à 015 ont été rédigées a posteriori
  le 03/11/2026 ; leur date de décision vient de l'historique git.
- **Nouvelle dépendance ou nouveau service externe** : une fiche avant la pull request.
- Ce qui relève de la cliente (règles métier, tarifs, périmètre) va dans
  [decisions.md](../decisions.md), pas ici.

## Modèle

```markdown
# NNN. Titre

- **Statut** : Proposée | Acceptée | Remplacée par NNN
- **Date** : décidée le JJ/MM/AAAA
- **Voir aussi** : documents ou fiches liés

## Contexte
Le problème, les contraintes (réseau faible, public, équipe, délais).

## Décision
Ce qu'on fait, en une ou deux phrases, puis le détail utile.

## Alternatives écartées
- **Option** : pourquoi pas.

## Conséquences
Ce que ça rend facile, ce que ça coûte, ce qu'il faudra surveiller.
```

## Liste

| N° | Décision | Statut | Date |
|---|---|---|---|
| [001](001-flask-pydantic-openapi.md) | Flask, Pydantic et un OpenAPI généré pour le back | Acceptée | 06/10/2026 |
| [002](002-couches-et-repositories.md) | Couches contrôleur, service, repository ; SQLAlchemy | Acceptée | 06/10/2026 |
| [003](003-session-jwt-cookies.md) | Session en JWT dans des cookies HttpOnly, CSRF par double envoi | Acceptée | 19/10/2026 |
| [004](004-mots-de-passe-scrypt.md) | Mots de passe et codes hachés en scrypt, avec limites d'essais | Acceptée | 19/10/2026 |
| [005](005-codes-sms.md) | Inscription et mot de passe oublié par code SMS | Acceptée | 02/11/2026 |
| [006](006-sms-simules.md) | SMS simulés dans les logs, sans donnée personnelle | Acceptée | 02/11/2026 |
| [007](007-etat-en-memoire.md) | Limites, verrous et inscriptions en attente en mémoire | Acceptée | 02/11/2026 |
| [008](008-mysql.md) | MySQL 8.4 plutôt que PostgreSQL et PostGIS | Acceptée, confirmée par l'équipe BD le 03/11/2026 | 20/10/2026 |
| [009](009-openrouteservice.md) | OpenRouteService pour les adresses et la distance | Acceptée | 02/11/2026 |
| [010](010-react-vite-pwa.md) | React, Vite et PWA, CSS maison sans framework | Acceptée | 06/10/2026 |
| [011](011-types-generes.md) | Types TypeScript générés depuis l'OpenAPI | Acceptée | 06/10/2026 |
| [012](012-objectif-regular-2g.md) | Objectif réseau « Regular 2G » pour chaque fonctionnalité | Acceptée | 20/10/2026 |
| [013](013-traductions-maison.md) | Textes dans des fichiers de traduction maison | Acceptée | 03/11/2026 |
| [014](014-socket-io.md) | Socket.IO pour le temps réel | Proposée | – |
| [015](015-leaflet-openstreetmap.md) | Leaflet et OpenStreetMap pour la carte | Proposée | – |
| [016](016-vitest.md) | Vitest pour les tests du front | Acceptée | 03/11/2026 |
