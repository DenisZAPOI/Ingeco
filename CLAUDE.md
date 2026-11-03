# En route pour l'emploi

Démonstrateur d'une plateforme d'accès à l'emploi en Guyane, construite autour d'un service de VTC solidaire, pour le client Ingeco Territoires (association loi 1901, selon le cahier des charges). Projet de BUT 3, IUT de Montreuil.

Elle aide une personne à s'orienter (questionnaire et plan d'action), à trouver une offre d'emploi, une formation ou un service d'aide, et surtout à s'y rendre : elle met en relation usagers et chauffeurs pour les trajets vers l'emploi, la formation, les soins et les démarches administratives. Des structures partenaires (associations, collectivités, entreprises) peuvent financer tout ou partie d'un trajet via des bons solidaires.

## Documents à lire

- **[docs/cahier-des-charges-v1.0.docx](docs/cahier-des-charges-v1.0.docx)** : cahier des charges reçu le 03/11/2026 (version 1.0, 14/10/2026). **C'est la source de vérité** : quand il contredit un autre document (expression des besoins, réponses antérieures du client, contrat d'API, nos hypothèses), il l'emporte, sans poser de question à la cliente. On ne lui pose que ce qu'il ne tranche pas, ce qu'il laisse à son choix, ou ce qui reste flou. Sujet générique d'une « plateforme 360° d'accès à l'emploi » en dix modules (M0 à M10) et trois paliers (P1 à P3). **Notre périmètre** (décidé le 03/11/2026) : **tout le palier P1**, sur tous les modules qui en ont un (partie « Périmètre » ci-dessous). Ses exigences transverses s'appliquent (partie « Règles du cahier des charges » ci-dessous) ; ce qu'il fixe est repris dans [docs/decisions.md](docs/decisions.md#ce-que-fixe-le-cahier-des-charges-v10).
- **[docs/expression-des-besoins.pdf](docs/expression-des-besoins.pdf)** : expression des besoins du client (version 1, 06/07/2026), centrée sur le VTC solidaire. Antérieure au cahier des charges, qui prime en cas de désaccord.
- **[README.md](README.md)** : présentation, lancement du projet, et guide pour l'équipe BD.
- **[docs/architecture.md](docs/architecture.md)** : organisation du code back et front, règles de chaque couche, contrat d'API, liste de contrôle pour ajouter une fonctionnalité. **À lire avant d'écrire du code.**

- **[docs/charte-graphique.md](docs/charte-graphique.md)** : couleurs, typographie, espacements, composants, ton des textes et accessibilité du front. **À suivre pour tout écran** ; les valeurs vivent dans `FRONTEND/src/styles/global.css`.
- **[docs/cas-d-utilisation.md](docs/cas-d-utilisation.md)** : cas d'utilisation par acteur, avec fiches détaillées, statut MVP et regroupement en fonctionnalités par étape. Résume les réponses du client qui ont fait passer le contrat d'API en version 2.
- **[docs/points-a-valider-porteur.pdf](docs/points-a-valider-porteur.pdf)** : choix et questions soumis au client (13/10/2026), avec ce qu'il a déjà confirmé.
- **[docs/contrat-api.md](docs/contrat-api.md)** : proposition de contrat d'API (routes, données, règles) remise à l'équipe BD pour concevoir le schéma. Version 2, intègre les réponses du client du 13/10/2026 et de la première visio ; les autres hypothèses restent non validées.
- **[docs/decisions.md](docs/decisions.md)** : ce qui est décidé (03/11/2026) et la valeur provisoire appliquée à chaque point non tranché, repérable dans le code par `CHANGER_SELON_DECISION`. **Référence pour la suite** : il prime sur les hypothèses des autres documents.
- **[docs/adr/](docs/adr/README.md)** : fiches de décision d'architecture, une par choix technique (Flask, MySQL, OpenRouteService, JWT en cookies, Regular 2G…), avec les alternatives écartées.
- **[docs/compte-rendu-visio-1.md](docs/compte-rendu-visio-1.md)** : décisions de la première visio avec la cliente (zone du pilote, profil du chauffeur, abonnement, organisation).

## Équipe et responsabilités

- **2 développeurs** (dont Denis ZAPOI) : front et back, c'est-à-dire tout ce repo.
- **3 étudiants parcours C** : la base de données, c'est-à-dire **tout le dossier `sql/`** : schéma, migrations (`sql/migrations/NNN_*.sql`), données de référence et de test, index, et les requêtes lourdes livrées en vues SQL (statistiques, chauffeurs proches, consommation des bons). Plus la partie base de `compose.yaml`. Détail dans le README, partie 5.
- **Côté client** : la fondatrice et présidente d'Ingeco Territoires, et une tutrice, Sophonie Delva, pour les questions numériques. Revue chaque mardi à 10 h, échanges par WhatsApp.
- **Échéances** :
  - **soutenance de la SAÉ le lundi 14 ou le mardi 15 décembre 2026** (à confirmer), environ 15 minutes, chacun présente sa partie. Gel des fonctionnalités le 10/12 ;
  - fin du projet pour la cliente vers le 10 janvier 2027 : un **démonstrateur** documenté et transmis (note de transmission, accès remis), pas un service en production (cahier des charges §1).
- **SAÉ S5 (IUT)** : un prototype fonctionnel répondant aux objectifs fixés avec la cliente. Fonctionnalités citées par l'IUT pour Ingeco : comptes, réservation, géolocalisation des chauffeurs, suivi en temps réel, paiement sécurisé, notifications, évaluation. Le « suivi en temps réel » s'y entend comme le **statut du trajet mis à jour en direct**, sans position GPS du chauffeur sur une carte : le cahier des charges met le suivi GPS en temps réel hors périmètre (décision du 03/11/2026, [docs/decisions.md](docs/decisions.md)). Notation : soutenance /20, rendu (rapport, base, code) /20, avis de la cliente /20. Rendus : rapport de gestion (répartition des tâches, temps de chacun, réunions, démos), application, code, fichiers SQL, documentation. Au moins une réunion avec la cliente toutes les deux semaines, avec un compte rendu.

La base ne nous appartient pas. **Les développeurs ne modifient plus aucun fichier de `sql/`** (décidé le 03/11/2026) : ni table, ni colonne, ni migration, ni donnée de test (et jamais de `Base.metadata.create_all()`). Si une fonctionnalité demande un changement de schéma, une vue ou une donnée, le signaler et rédiger la demande pour l'équipe BD (issue GitHub avec l'étiquette `bd` : besoin, table ou colonne suggérée, date), sans l'appliquer.

Partage des requêtes : les développeurs écrivent les requêtes courantes en SQLAlchemy dans `repository/` ; l'équipe BD écrit les requêtes lourdes en **vues SQL**, que `repository/` lit comme des tables. Les classes de `models/` suivent exactement le schéma et les migrations de l'équipe BD.

## Stack

Le socle reprend celui de ProjectOrganizer (R5.A.05), que Denis connaît déjà.

- **Back** : Python 3.14, Flask, Flask-SocketIO, SQLAlchemy, Pydantic + flask-pydantic-spec (validation et Swagger). Versions figées dans `BACKEND/requirements.txt`.
- **Front** : React 19 + TypeScript 6, Vite 8, react-router-dom 7, PWA (vite-plugin-pwa), CSS maison sans framework. Leaflet + OpenStreetMap et socket.io-client seront ajoutés à l'étape 4.
- **Adresses et distance par la route** : OpenRouteService (données OpenStreetMap), appelé depuis `repository/place_repository.py`. Clé dans `ORS_API_KEY` ; sans clé, lieux factices et aucun appel à Internet (tests, CI). S'il ne répond pas : `503`, pas de prix.
- **Contrat d'API** : l'OpenAPI généré par le back. Les types TypeScript du front en sont **générés** (`npm run api:types`), jamais écrits à la main.
- **Auth** : JWT dans des cookies `HttpOnly` (Flask-JWT-Extended), jeton d'accès de 15 min renouvelé par un jeton de 30 jours, CSRF par double envoi, mots de passe hachés en scrypt (Werkzeug). Rôle contrôlé côté back par `@require_login(...)` (`utils/access.py`). Détail dans [docs/architecture.md](docs/architecture.md).
- **BD** : fournie par l'équipe parcours C. MySQL 8.4 (à confirmer avec eux), en local dans un conteneur Docker lancé depuis WSL (`compose.yaml`, port 3307, schéma `sql/schema-mvp.sql` ; `sql/schema-hors-scope.sql` n'est pas chargé). Pilote PyMySQL. Les `repository/` sont encore sur données factices en mémoire. Les tests et la CI tournent sur SQLite en mémoire. Le déploiement sera choisi en fin de projet. Le guide pour l'équipe BD est dans le README (partie 5) : le tenir à jour.

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
    i18n/          # textes de l'interface : fr.ts, t() et tn()
    lib/           # logique pure, sans React
    hooks/         # appel + chargement + erreur + nouvelle tentative
    context/       # état global (session de l'utilisateur connecté)
    components/    # ui/, layout/, puis un dossier par domaine
    pages/         # une page par route
    routes/        # AppRoutes.tsx
    styles/        # global.css (variables)
sql/                     # à l'équipe BD : les développeurs n'y touchent pas
  schema-mvp.sql         # schéma v2 + données de référence, chargé dans le conteneur ; figé une fois validé par l'équipe BD
  migrations/            # (à venir) NNN_description.sql, un changement par fichier, jamais modifié une fois mergé
  demo-data.sql          # comptes et courses de test (mot de passe public), local seulement
  schema-hors-scope.sql  # bons, structures, documents, formation : pas encore chargé
compose.yaml             # base MySQL locale (Docker)
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
# base MySQL locale (Docker, compose.yaml ; .env à la racine copié de .env.example)
docker compose up -d
docker compose down -v                     # efface la base, rechargée depuis sql/ au prochain up

# back (http://localhost:5000, Swagger sur /apidoc/swagger)
cd BACKEND && .venv/Scripts/python -m app
cd BACKEND && .venv/Scripts/python -m pytest

# front (http://localhost:5173)
cd FRONTEND && npm run dev
cd FRONTEND && npm run lint
cd FRONTEND && npm run lint:texts          # aucun texte d'interface écrit dans le code
cd FRONTEND && npm test                    # Vitest : traductions, formats, dates
cd FRONTEND && npm run build
cd FRONTEND && npm run api:types           # back lancé : régénère src/types/api.ts
```

Avant de rendre la main : `pytest`, `npm test`, `npm run lint`, `npm run lint:texts`, `npm run build`, puis test dans le navigateur, **dont un passage en « Regular 2G »** (voir ci-dessous).

La CI GitHub (`.github/workflows/ci.yml`) relance ces vérifications sur chaque pull request, plus la comparaison des types générés (`npm run api:types`) : elles doivent passer pour merger sur `main`.

## Règles d'architecture

Le détail est dans [docs/architecture.md](docs/architecture.md). L'essentiel :

- Un contrôleur appelle un service, un service appelle un repository. Aucune requête BD hors de `repository/`. C'est ce qui permet de passer des données factices à la vraie base sans toucher au reste.
- Un service ne connaît pas Flask : il lève une erreur de `utils/errors.py`, traduite en `{ error, detail }` avec le bon code.
- JSON en camelCase (traduit par `dtos/base.py`), champs vides envoyés à `null`. Chaque route déclare tous ses codes d'erreur dans `@spec.validate`.
- Chaque route vérifie le rôle de l'appelant côté back. Le front masque des écrans, il ne protège rien.
- Le front doit rester léger et tolérer un réseau faible : peu de dépendances, pas de ressources lourdes, un état de chargement et un état d'erreur avec nouvelle tentative sur chaque appel (`RequestState`).
- **Objectif réseau : « Regular 2G »** (profil des DevTools : 250 kbit/s, 300 ms d'aller-retour), vérifié pour **chaque fonctionnalité** avant sa pull request. Sur ce profil : quelque chose d'utile à l'écran en moins de 1 s, un écran utilisable en moins de 5 s à la première visite, une réouverture sans attente. Moyens (chargement optimiste, allers-retours comptés, messages de réseau lent) et méthode de test : [docs/architecture.md](docs/architecture.md#réseau-faible--objectif-regular-2g).
- L'interface est pensée pour un public peu à l'aise avec le numérique : parcours courts, gros boutons, textes simples, accessible aux personnes à mobilité réduite.

## Règles du cahier des charges (v1.0)

Exigences transverses du [cahier des charges](docs/cahier-des-charges-v1.0.docx) (§ entre parenthèses), valables quel que soit le périmètre retenu avec la cliente.

**Données et droit**
- **Champs interdits** en base, dans les DTO et les formulaires : nationalité, situation administrative de séjour, numéro de sécurité sociale, origine, diagnostic médical (§12). Un besoin s'écrit comme un besoin (« véhicule accessible »), jamais comme un diagnostic. Le chauffeur ne voit jamais de justificatif social du passager (§7.4).
- **Aucune décision exclusivement automatique** sur l'éligibilité, l'orientation ou l'attribution d'une course (RGPD art. 22) : un humain peut toujours reprendre la main. Aucune IA de tri de personnes ni d'évaluation d'éligibilité (§13.1).
- On ne demande que ce qui sert, au moment où ça sert (minimisation, §2).

**Comportement**
- **Jamais de fausse confirmation** : le chargement optimiste sert à afficher vite, jamais à annoncer une demande comme reçue avant la réponse du serveur. Un paiement échoué n'apparaît jamais comme réussi ; un double clic ne crée ni doublon ni double débit (§6, §7.4).
- Une course n'est jamais « confirmée » sans chauffeur affecté, et n'est attribuée qu'à un seul chauffeur (§7.4).
- Une demande refusée (hors zone, hors horaire) l'est **avec une explication** en langage simple (§18).
- **Dates et rappels calculés dans le fuseau `America/Cayenne`**, côté back comme côté front, avec des tests automatisés sur les dates (§3). Le back stocke en UTC et convertit pour toute règle qui dépend du jour ou de l'heure locale.

**Interface**
- **Tous les textes d'interface dans `FRONTEND/src/i18n/fr.ts`**, affichés par `t('cle')` (ou `tn` pour un pluriel), jamais écrits en dur dans les composants ni gardés dans une constante de module, pour pouvoir ajouter une langue sans toucher au code (P1, §6). `npm run lint:texts` le vérifie. Le français reste la seule langue tant que la cliente n'en fournit pas d'autre ; les messages métier du back restent en français (ADR 013).
- **Au plus 3 actions principales par écran**, une icône toujours accompagnée d'un texte, la couleur seule ne porte jamais une information (§6, §10). Accueil organisé par besoins (« J'ai besoin d'un trajet »), pas par fonctionnalités.
- La mention **« Projet étudiant — démonstrateur »** reste visible dans l'application, et une page « À propos » crédite les auteurs (§14). Le nom et le logo d'Ingeco Territoires ne s'utilisent qu'avec l'accord de la cliente.
- Aucun service d'urgence n'est promis dans les textes (§6).

**Projet**
- **Une ADR par choix technique** ([docs/adr/](docs/adr/README.md), `NNN-titre.md` : contexte, décision, alternatives, conséquences), écrite avant la pull request de toute nouvelle dépendance ou de tout nouveau service externe. Une fiche acceptée ne se réécrit pas : une nouvelle la remplace (§11).
- **Outils libres ou gratuits uniquement**, aucune carte bancaire personnelle (§20). Toute nouvelle dépendance : licence compatible, notée dans l'inventaire des dépendances (§14, §17).
- **Comptes des services externes** (GitHub, OpenRouteService, hébergement, paiement, SMS) ouverts au nom d'Ingeco ou de l'IUT, et remis à la fin du projet (§20) : tout nouveau service s'ajoute d'abord au tableau du README, partie « Comptes des services externes ».
- Le **guide de lancement pas à pas** en tête du README s'adresse à des personnes peu à l'aise avec l'informatique : le mettre à jour à chaque changement d'installation ou de lancement.
- Objectif d'**installation en une commande** (Docker Compose : base, back et front) et de données de démonstration générées par script (§11, §17).
- L'**usage de l'IA générative** (dont Claude Code) est déclaré dans le rapport ; aucune donnée confidentielle transmise à un outil tiers (§14).
- Les maquettes ou la démo d'un parcours sont montrées à la cliente avant de le considérer comme fini (§10).

## Rôles

| Rôle | Ce qu'il fait |
|---|---|
| Usager | Réserve, paie, évalue un trajet |
| Usager prioritaire | Idem, avec prise en charge partielle ou totale, et accès par téléphone |
| Chauffeur | Gère ses disponibilités, accepte et clôture des courses, suit ses revenus. Son compte est créé par l'administrateur après vérification de ses documents en personne |
| Référent partenaire | Émet des bons solidaires, suit leur consommation (associations, collectivités, entreprises) |
| Opérateur | Centre d'appel : retrouve ou crée un usager, réserve et annule à sa place |
| Administrateur | Gère les comptes, les tarifs, les statistiques, le support |

## Périmètre

Fixé par le [cahier des charges](docs/cahier-des-charges-v1.0.docx) (§5, §7, §18). **Décidé le 03/11/2026 : tout le palier P1**, c'est-à-dire la part P1 de chaque module qui en a une : socle (M0), orientation (M1), emploi (M2), formation (M3), mobilité (M4), freins et annuaire (M5), administration (M9). Les modules M6, M7, M8 et M10 n'ont rien au palier P1. Des éléments du P2 viennent après la soutenance. Le détail, exigence par exigence, est dans [docs/decisions.md](docs/decisions.md#ce-que-fixe-le-cahier-des-charges-v10).

**Le fil rouge** : le scénario A du cahier des charges (§8), à dérouler de bout en bout en démonstration. Jordan, 22 ans, sans permis : questionnaire, plan d'action, offre proche, « Comment y aller ? », trajet pour l'entretien, puis trajets du premier mois. Accueil organisé par besoins : « Je cherche un travail », « J'ai besoin d'un trajet », « J'ai besoin d'aide ».

**Palier P1, avant le gel du 10/12** (✓ fait)
- M0, socle : compte par téléphone sans courriel obligatoire, code simulé ✓, récupération par téléphone ✓, demande de suppression ; rôles ✓ ; textes dans des fichiers de traduction ✓ et changement de langue ; PWA installable ✓ ; accessibilité de base (contrastes, libellés, clavier) ; aide (« Être rappelé », FAQ, signaler un problème).
- M1, orientation : questionnaire court et visuel (situation, projet, expériences y compris informelles, disponibilités, freins exprimés en besoins, langue, équipement numérique), puis « Mon plan d'action » en 3 à 5 étapes, calculé par des règles simples, avec les services proposés et un contact humain. Aucune décision automatique, aucun diagnostic médical ni situation administrative.
- M2, emploi : jeu d'offres fictives ; filtres par commune, horaires, débutant accepté, sans diplôme ; sur chaque offre, « Comment y aller ? » ouvre une demande de trajet en 3 actions au plus, motif prérempli.
- M3, formation : liens vers des catalogues de formation existants.
- M5, annuaire : services d'aide fictifs (garde, logement, droits, santé, aide alimentaire, numérique, démarches, équipement) avec langues parlées, horaires, accessibilité et date de mise à jour ; fiches pratiques « Comment faire ? » en langage simple.
- M4, passager : départ et arrivée par adresse ✓, repère ou point sur carte ; date et horaire ✓, passagers, bagages, besoin d'un véhicule adapté ✓ ; zones ✓ et horaires autorisés ; prix ✓, réduction, reste à payer et conditions d'annulation affichés avant envoi ; version du tarif conservée ✓ ; numéro unique et « en attente de chauffeur » ✓ ; motif ✓ ; historique ✓, chauffeur et véhicule ✓.
- M4, chauffeur : dossier (véhicule ✓, places, zones, disponibilités, pièces), activation après validation ✓, suspension à l'expiration des pièces ; propositions avec délai de réponse, acceptation ou refus ; une course à un seul chauffeur ✓ ; arrivée, début ✓, fin ✓, absence, incident horodatés avec leur auteur.
- M4, états : demande envoyée, attente de chauffeur ✓, confirmée ✓, chauffeur arrivé, en cours ✓, terminée ✓ ; refusée faute de disponibilité ✓ (expiration), annulée ✓, passager absent. Paiement : en attente ✓, payé ✓, échoué, remboursé ✓.
- M9, administration : utilisateurs ✓, chauffeurs ✓, zones, horaires, tarifs ; affectation et réaffectation d'une course, avec avertissement du passager.
- Demandé par la SAÉ : évaluation du trajet ✓ ; statut du trajet mis à jour en direct (son « suivi en temps réel »), **sans suivi GPS**.
- Projet : maquettes de tous les parcours validées par la cliente, installation en une commande, données de démo par script, licence et AUTHORS ✓, inventaire des dépendances, registre simplifié des traitements et matrice des flux, tests sur prix et états ✓.

**Palier P2, après la soutenance** (selon le temps, par ordre de priorité proposé)
- Tarifs solidaires, plafonds, tiers payeur et codes de trajet (les bons solidaires) ; éligibilité validée par un prescripteur (motif, validité, plafond), enveloppes par financeur, chaque trajet imputé à un seul financeur.
- Réservation pour le compte d'une personne (prescripteur, accompagnant ou centre d'appel), avec son accord tracé et révocable.
- Notifications simulées (SMS dans un journal, notifications web, courriel de test), règles d'annulation et d'absence réglables, langue de démonstration, « Pourquoi cette proposition ? » sur le plan d'action.

**Simulé** : paiement (aucune transaction réelle), SMS (écrits dans les logs, sans numéro ni contenu personnel).

**Hors périmètre** (cahier des charges §5) : suivi GPS en temps réel, données réelles, paiements réels, envoi massif de SMS, mise en ligne ouverte au public, applications sur les stores, décision automatisée et IA de tri. Aussi hors du projet : formation et agréments des chauffeurs, abonnement mensuel (absent du cahier des charges).

Ne rien implémenter hors de ce périmètre sans demande explicite.

## Ordre de développement

0. ~~Socle back et front~~ (fait : couches, `/health`, page `/diagnostic`, tests, génération des types)
1. Modèle de données et contrat d'API, en accord avec l'équipe BD (en cours : contrat v2, schéma v2 dans `sql/` à faire relire par l'équipe BD)
2. Authentification et rôles (fait : inscription, connexion, activation, profil, administration des comptes UC51 à UC53 ; reste : création des référents partenaires, avec les bons après la soutenance)
3. ~~Parcours de réservation de bout en bout, sur données factices~~ (fait : réservation immédiate ou programmée, estimation, paiement simulé, page du trajet, mes trajets, annulation, évaluation, côté chauffeur (disponibilité, position, offres, accepter, se désister, démarrer, terminer), expiration des courses (UC60, tâche chaque minute dans `utils/periodic.py`), revenus du chauffeur (UC28)). Rien n'est en temps réel : les écrans ont un bouton « Actualiser »
4. Sprint 1 (04/11 → 17/11) : ce qui **ne demande pas de changement de base**, sur données factices en mémoire comme les trajets : maquettes des nouveaux parcours, montrées à la cliente ; accueil par besoins ; offres d'emploi avec filtres et « Comment y aller ? » ; liens vers les formations ; annuaire des aides et fiches pratiques ; côté trajets, affectation et réaffectation par l'administrateur, délai de réponse et refus d'une offre, conditions d'annulation avant envoi, photo du chauffeur ; changement de langue, FAQ ; installation en une commande (Docker Compose). Demander dès le début à l'équipe BD les tables et colonnes du sprint 2
5. Sprint 2 (18/11 → 01/12) : branchement sur la vraie base MySQL, y compris les nouvelles tables (offres, services, fiches, questionnaires et plans d'action) ; questionnaire d'orientation et plan d'action ; horaires, zones et tarifs réglables par l'administrateur ; repère, point sur carte et passagers ; états « chauffeur arrivé » et « passager absent », paiement échoué, auteur des étapes ; pièces du chauffeur et suspension ; demande de suppression de compte, « Être rappelé », signalement
6. Sprint 3 (02/12 → 10/12) : statut du trajet mis à jour en direct (Socket.IO : `ride:updated`, `ride:offer`, sans position GPS) ; accessibilité de base ; données de démo par script ; dossier conformité (registre des traitements, matrice des flux), licence et inventaire des dépendances ; répétition du scénario A ; finitions, gel le 10/12, puis démo et soutenance
7. Sprint 4, après la soutenance (16/12 → 10/01) : éléments du P2 (bons solidaires, réservation pour le compte d'une personne), puis livrables de transmission (guides, vidéo, note de transmission, remise des accès)

Le détail des sprints et les questions à poser pour chacun : [docs/questions-sprint-2026-11-04.md](docs/questions-sprint-2026-11-04.md).

## Conventions

- Identifiants de code en anglais (`ride`, `driver`, `voucher`, `ride_service.py`), textes d'interface en français. Documentation en français.
- Fichiers back : `<resource>_controller.py`, `<resource>_service.py`, `<resource>_repository.py`, `<resource>_dto.py`. Front : composants en `PascalCase.tsx` (export nommé), hooks en `useSomething.ts`, pages en `SomethingPage.tsx`.
- Pas de nombre magique : une constante nommée. Les commentaires expliquent le pourquoi, pas le quoi. Jamais `any` en TypeScript.
- Pas de push direct sur `main`. Une branche par fonctionnalité (`feature/...`, `fix/...`, `perf/...` pour la performance), une pull request relue par l'autre développeur.
- Messages de commit courts, à l'impératif, préfixés (`feat:`, `fix:`, `perf:`, `docs:`, `refactor:`, `test:`, `chore:`).
- Toute logique de `services/` a ses tests pytest, dont au moins un qui prouve qu'un rôle non autorisé est refusé.
- Secrets dans `.env`, jamais commités. Tenir les `.env.example` à jour.
- RGPD : aucune donnée personnelle réelle dans les jeux de test, les seeds ou les logs.

## Points à confirmer

- **Avec l'équipe BD** : relecture et validation du schéma v2 (`sql/`) **pour le 17/11** (il devient ensuite le point de départ des migrations), réécrit par les développeurs à partir de leur première version (écrite avant le contrat v2) ; confirmation de MySQL 8.4 ; stockage de la photo du chauffeur (H19) ; vues des statistiques pour le sprint 3 ; hébergement de la base en production (choisi en fin de projet). Liste complète dans le README, partie 5.
- **Avec le client** : les contenus des nouveaux modules (services d'aide, offres types, questions du questionnaire), la validation des maquettes, la langue de démonstration et ses textes, la licence (MIT ou EUPL 1.2, ou cession) et la convention tripartite, l'usage du nom et du logo d'Ingeco, la fiche de cadrage (§21). Questions dans [docs/questions-sprint-2026-11-04.md](docs/questions-sprint-2026-11-04.md#le-cahier-des-charges-v10).
- **Avec le client** : les valeurs des réglages que le cahier des charges rend paramétrables (horaires autorisés, délai de réponse du chauffeur, délai d'annulation gratuite, frais ensuite, règle d'absence). En attendant, valeurs provisoires de [docs/decisions.md](docs/decisions.md).
- **Avec le client** : les montants et règles des bons solidaires (P2, après la soutenance), dans le cadre fixé par le cahier des charges (éligibilité, plafond, enveloppe par financeur).
- **Avec le client** : le centre d'appel est tenu par des personnes dédiées, et tout le monde peut réserver par téléphone (donnés comme confirmés le 13/10/2026, mais absents de la première visio : retrouver la trace écrite de cette réponse). Le contrat v2 leur donne un rôle `operator` sans droits d'administration : à confirmer, ainsi que ce qu'elles peuvent faire en plus de réserver (question 2).
- **Avec le client** : le contenu exact de la zone du pilote. Les zones sont réglables par l'administrateur (cahier des charges) ; valeur provisoire : Cayenne, Rémire-Montjoly et Matoury.
- **Avec le client** (audit de sécurité du 02/11/2026, [docs/audit-securite-2026-11-02.md](docs/audit-securite-2026-11-02.md)) : le plafond de 1 course immédiate et 3 programmées non terminées par usager, et le motif du trajet visible du chauffeur sur une offre.
- **Avec l'équipe BD** : la colonne `version_session` sur `utilisateur` (leur première migration) et la séparation de `sql/demo-data.sql` (README, partie 5).
- **Au déploiement** : `TRUSTED_PROXY_COUNT` selon l'hébergement ; les inscriptions en attente, les limites d'essais et les verrous sont en mémoire, valables pour un seul processus d'API.
- **Avec le client** : les montants du tarif (8 € de prise en charge + 0,80 €/km dans `sql/schema-mvp.sql` et les données factices sont provisoires).
- **En interne** : les quotas gratuits d'OpenRouteService et l'obligation éventuelle de citer la source (non confirmés : à vérifier sur le compte avant la mise en service), puis valider l'appel réel avec une clé (testé seulement avec de fausses réponses).
- **En interne** : la géolocalisation en arrière-plan côté chauffeur est peu fiable en PWA. Si elle devient indispensable, il faudra une appli native pour le chauffeur.
