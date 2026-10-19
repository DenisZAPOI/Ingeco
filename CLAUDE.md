# En route pour l'emploi

Application de VTC solidaire en Guyane, pour le client Ingeco Territoires (SAS à mission). Projet de BUT 3, IUT de Montreuil.

Elle met en relation usagers et chauffeurs pour les trajets vers l'emploi, la formation, les soins et les démarches administratives. Des structures partenaires (associations, collectivités, entreprises) peuvent financer tout ou partie d'un trajet via des bons solidaires.

## Documents à lire

- **[docs/expression-des-besoins.pdf](docs/expression-des-besoins.pdf)** : cahier des charges du client (version 1, 06/07/2026).
- **[README.md](README.md)** : présentation, lancement du projet, et guide pour l'équipe BD.
- **[docs/architecture.md](docs/architecture.md)** : organisation du code back et front, règles de chaque couche, contrat d'API, liste de contrôle pour ajouter une fonctionnalité. **À lire avant d'écrire du code.**

- **[docs/charte-graphique.md](docs/charte-graphique.md)** : couleurs, typographie, espacements, composants, ton des textes et accessibilité du front. **À suivre pour tout écran** ; les valeurs vivent dans `FRONTEND/src/styles/global.css`.
- **[docs/cas-d-utilisation.md](docs/cas-d-utilisation.md)** : cas d'utilisation par acteur, avec fiches détaillées, statut MVP et regroupement en fonctionnalités par étape. Résume les réponses du client qui ont fait passer le contrat d'API en version 2.
- **[docs/points-a-valider-porteur.pdf](docs/points-a-valider-porteur.pdf)** : choix et questions soumis au client (13/10/2026), avec ce qu'il a déjà confirmé.
- **[docs/contrat-api.md](docs/contrat-api.md)** : proposition de contrat d'API (routes, données, règles) remise à l'équipe BD pour concevoir le schéma. Version 2, intègre les réponses du client du 13/10/2026 ; les autres hypothèses restent non validées.

## Équipe et responsabilités

- **2 développeurs** (dont Denis ZAPOI) : front et back, c'est-à-dire tout ce repo.
- **3 étudiants parcours C** : la base de données (schéma, migrations, données de référence).

La base ne nous appartient pas. Ne jamais créer ni modifier de table, de colonne ou de migration depuis ce repo (jamais de `Base.metadata.create_all()`). Si une fonctionnalité demande un changement de schéma, le signaler et rédiger la demande pour l'équipe BD, sans l'appliquer.

## Stack

Le socle reprend celui de ProjectOrganizer (R5.A.05), que Denis connaît déjà.

- **Back** : Python 3.14, Flask, Flask-SocketIO, SQLAlchemy, Pydantic + flask-pydantic-spec (validation et Swagger). Versions figées dans `BACKEND/requirements.txt`.
- **Front** : React 19 + TypeScript 6, Vite 8, react-router-dom 7, PWA (vite-plugin-pwa), CSS maison sans framework. Leaflet + OpenStreetMap et socket.io-client seront ajoutés à l'étape 4.
- **Contrat d'API** : l'OpenAPI généré par le back. Les types TypeScript du front en sont **générés** (`npm run api:types`), jamais écrits à la main.
- **Auth** : JWT dans des cookies `HttpOnly` (Flask-JWT-Extended), jeton d'accès de 15 min renouvelé par un jeton de 30 jours, CSRF par double envoi, mots de passe hachés en scrypt (Werkzeug). Rôle contrôlé côté back par `@require_login(...)` (`utils/access.py`). Détail dans [docs/architecture.md](docs/architecture.md).
- **BD** : fournie par l'équipe parcours C (SGBD à confirmer). En local, SQLite vide (`sqlite:///local.db`) ou données factices dans `repository/` tant que le schéma n'est pas livré. SQLite n'est qu'un branchement temporaire (plus permissif que les vrais SGBD) : dès que le SGBD est connu, travailler en local sur le même SGBD et retirer SQLite. Le guide pour l'équipe BD est dans le README (partie 5) : le tenir à jour.

## Structure du repo

```
BACKEND/
  app/
    controllers/   # un Blueprint par ressource : HTTP ↔ service
    dtos/          # modèles Pydantic d'entrée/sortie (base.py : camelCase, format d'erreur)
    services/      # règles métier, droits, transactions
    repository/    # seul endroit qui parle à la BD
    models/        # modèles ORM des tables livrées par l'équipe BD (vide pour l'instant)
    sockets/       # événements temps réel
    utils/         # database, errors, logs, request_logs, security_headers
    main.py        # create_app()
    config.py      # lecture du .env
  tests/
FRONTEND/
  src/
    api/           # client.ts (le seul fetch) + une fonction par appel
    types/api.ts   # généré depuis l'OpenAPI du back
    lib/           # logique pure, sans React
    hooks/         # appel + chargement + erreur + nouvelle tentative
    context/       # état global (session de l'utilisateur connecté)
    components/    # ui/, layout/, puis un dossier par domaine
    pages/         # une page par route
    routes/        # AppRoutes.tsx
    styles/        # global.css (variables)
docs/
```

Modèle à recopier pour une nouvelle fonctionnalité : la route `GET /health`, qui traverse toutes les couches (back) et la page `/diagnostic` (front).

## Commandes

Première installation :

```
cd BACKEND && python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt
cp BACKEND/.env.example BACKEND/.env        # puis générer FLASK_SECRET_KEY
cd FRONTEND && npm install && cp .env.example .env
```

Au quotidien :

```
# back (http://localhost:5000, Swagger sur /apidoc/swagger)
cd BACKEND && .venv/Scripts/python -m app
cd BACKEND && .venv/Scripts/python -m pytest

# front (http://localhost:5173)
cd FRONTEND && npm run dev
cd FRONTEND && npm run lint
cd FRONTEND && npm run build
cd FRONTEND && npm run api:types           # back lancé : régénère src/types/api.ts
```

Avant de rendre la main : `pytest`, `npm run lint`, `npm run build`, puis test dans le navigateur.

## Règles d'architecture

Le détail est dans [docs/architecture.md](docs/architecture.md). L'essentiel :

- Un contrôleur appelle un service, un service appelle un repository. Aucune requête BD hors de `repository/`. C'est ce qui permet de passer des données factices à la vraie base sans toucher au reste.
- Un service ne connaît pas Flask : il lève une erreur de `utils/errors.py`, traduite en `{ error, detail }` avec le bon code.
- JSON en camelCase (traduit par `dtos/base.py`), champs vides envoyés à `null`. Chaque route déclare tous ses codes d'erreur dans `@spec.validate`.
- Chaque route vérifie le rôle de l'appelant côté back. Le front masque des écrans, il ne protège rien.
- Le front doit rester léger et tolérer un réseau faible : peu de dépendances, pas de ressources lourdes, un état de chargement et un état d'erreur avec nouvelle tentative sur chaque appel (`RequestState`).
- L'interface est pensée pour un public peu à l'aise avec le numérique : parcours courts, gros boutons, textes simples, accessible aux personnes à mobilité réduite.

## Rôles

| Rôle | Ce qu'il fait |
|---|---|
| Usager | Réserve, paie, évalue un trajet |
| Usager prioritaire | Idem, avec prise en charge partielle ou totale, et accès par téléphone |
| Chauffeur | Gère ses disponibilités, accepte et clôture des courses, suit ses revenus. Son compte est créé par l'administrateur après vérification de ses documents en personne |
| Référent partenaire | Émet des bons solidaires, suit leur consommation (associations, collectivités, entreprises) |
| Opérateur | Centre d'appel : retrouve ou crée un usager, réserve et annule à sa place |
| Administrateur | Gère les comptes, les tarifs, les statistiques, le support |

## Périmètre du MVP

À faire valider par le client avant de s'y tenir.

**Dans le MVP**
- Création de compte et connexion
- Réservation immédiate ou programmée
- Mise en relation avec un chauffeur disponible
- Côté chauffeur : accepter, démarrer, clôturer une course
- Suivi du trajet sur carte
- Évaluation du trajet
- Bons solidaires : émission, utilisation à la réservation, suivi de consommation
- Écran opérateur pour réserver au nom d'un usager (tient lieu de centre d'appel)
- Statistiques administrateur de base

**Simulé**
- Paiement : mode test du prestataire, aucun paiement réel
- SMS : écrits dans les logs, pas envoyés (sans le numéro ni le contenu personnel, RGPD)

**Hors MVP**
- Paiement en espèces dans l'application (exclu par le cahier des charges)
- Module de formation des chauffeurs
- Facturation consolidée des partenaires
- Application native

**Demandé par le cahier des charges, pas encore classé** (à trancher avec le client)
- Tarification solidaire modulable (selon le profil et le financement) et paramétrage des tarifs par l'administrateur
- Notifications à l'usager
- Gestion documentaire des chauffeurs (permis, assurance, agréments)
- Indicateurs d'impact social et couverture territoriale dans le tableau de bord

Ne pas implémenter d'élément hors MVP ou non classé sans demande explicite.

## Ordre de développement

0. ~~Socle back et front~~ (fait : couches, `/health`, page `/diagnostic`, tests, génération des types)
1. Modèle de données et contrat d'API, en accord avec l'équipe BD
2. Authentification et rôles
3. Parcours de réservation de bout en bout, sur données factices
4. Temps réel et carte
5. Bons solidaires
6. Écran opérateur
7. Statistiques administrateur

## Conventions

- Identifiants de code en anglais (`ride`, `driver`, `voucher`, `ride_service.py`), textes d'interface en français. Documentation en français.
- Fichiers back : `<resource>_controller.py`, `<resource>_service.py`, `<resource>_repository.py`, `<resource>_dto.py`. Front : composants en `PascalCase.tsx` (export nommé), hooks en `useSomething.ts`, pages en `SomethingPage.tsx`.
- Pas de nombre magique : une constante nommée. Les commentaires expliquent le pourquoi, pas le quoi. Jamais `any` en TypeScript.
- Pas de push direct sur `main`. Une branche par fonctionnalité (`feature/...`, `fix/...`), une pull request relue par l'autre développeur.
- Messages de commit courts, à l'impératif, préfixés (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
- Toute logique de `services/` a ses tests pytest, dont au moins un qui prouve qu'un rôle non autorisé est refusé.
- Secrets dans `.env`, jamais commités. Tenir les `.env.example` à jour.
- RGPD : aucune donnée personnelle réelle dans les jeux de test, les seeds ou les logs.

## Points à confirmer

- **Avec l'équipe BD** : SGBD retenu (le pilote Python s'ajoute alors à `requirements.txt`), date de livraison du schéma, mode d'accès (connexion directe ou autre).
- **Avec le client** : disponibilité « 24h/24 » ou « en semaine avec créneaux élargis » (le cahier des charges dit les deux).
- **Avec le client** : « Android/iOS » ou « Android prioritaire » (idem).
- **Avec le client** : le centre d'appel est tenu par des personnes dédiées (confirmé le 13/10/2026). Le contrat v2 leur donne un rôle `operator` sans droits d'administration : à confirmer, ainsi que ce qu'elles peuvent faire en plus de réserver (question 2).
- **Avec le client** : les éléments « pas encore classés » du périmètre ci-dessus.
- **En interne** : la géolocalisation en arrière-plan côté chauffeur est peu fiable en PWA. Si elle devient indispensable, il faudra une appli native pour le chauffeur.
