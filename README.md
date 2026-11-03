# En route pour l'emploi

Créer une application de mise en relation entre usagers et chauffeurs afin de faciliter les
déplacements vers l'emploi, la formation, les soins, les démarches administratives et les
zones isolées de Guyane, avec une dimension sociale et inclusive.

Client : **Ingeco Territoires** (SAS à mission). Projet de BUT 3 Informatique, IUT de Montreuil.
Cahier des charges : [docs/expression-des-besoins.pdf](docs/expression-des-besoins.pdf).

Auteurs du projet :
- Denis ZAPOI
- Yanis OUADAH
- Baptiste DURAND-KEOHAVONG
- Kurtys TSHIBOLA
- Boude HANOUNE

Rôles dans [AUTHORS](AUTHORS), repris dans l'application (page « À propos »).

---

## Sommaire

1. [Le projet en bref](#1-le-projet-en-bref)
2. [Technologies](#2-technologies)
3. [Organisation du dépôt](#3-organisation-du-dépôt)
4. [Lancer le projet](#4-lancer-le-projet)
5. [Pour l'équipe base de données](#5-pour-léquipe-base-de-données)
6. [Règles de travail](#6-règles-de-travail)

---

## 1. Le projet en bref

L'application met en relation des **usagers** et des **chauffeurs** pour des trajets vers
l'emploi, la formation, les soins et les démarches. Des **structures partenaires**
(associations, collectivités, entreprises) peuvent financer tout ou partie d'un trajet grâce à
des **bons solidaires**.

| Profil | Ce qu'il fait |
|---|---|
| Usager | Réserve, paie, évalue un trajet |
| Usager prioritaire | Idem, avec prise en charge partielle ou totale |
| Chauffeur | Gère ses disponibilités, accepte et clôture des courses, suit ses revenus |
| Référent partenaire | Émet des bons solidaires, suit leur consommation |
| Opérateur | Centre d'appel : retrouve ou crée un usager, réserve et annule à sa place |
| Administrateur | Gère les comptes, les tarifs, les statistiques |

Répartition du travail :
- **Développement (2 personnes)** : le back-end et le front-end, c'est-à-dire ce dépôt.
- **Base de données (3 personnes, parcours C)** : le schéma, les scripts de création, les
  données de référence. Voir la [partie 5](#5-pour-léquipe-base-de-données).

## 2. Technologies

| Partie | Technologies |
|---|---|
| Back-end (API) | Python 3.14, Flask, Flask-SocketIO (temps réel), SQLAlchemy (accès à la base), Pydantic (validation), Flask-JWT-Extended (connexion) |
| Front-end | React 19, TypeScript, Vite, application web installable sur mobile (PWA) |
| Base de données | **MySQL 8.4**, en local dans Docker (choix de l'équipe BD, à confirmer) |
| Documentation de l'API | Générée automatiquement (Swagger) : http://localhost:5000/apidoc/swagger |

## 3. Organisation du dépôt

```
BACKEND/      L'API en Python
  app/
    controllers/   Reçoit les requêtes HTTP
    services/      Les règles métier
    repository/    Le SEUL endroit qui parle à la base de données
    models/        La description en Python des tables de l'équipe BD
  tests/
FRONTEND/     L'interface web (React)
sql/          Scripts de la base : schema-mvp.sql (chargé), schema-hors-scope.sql (pas encore)
docs/         Cahier des charges, architecture
compose.yaml  La base MySQL locale (Docker)
```

Le détail de l'organisation du code est dans [docs/architecture.md](docs/architecture.md).

## 4. Lancer le projet

Prérequis : **Python 3.14**, **Node.js 24**, et **Docker** pour la base de données (Docker
Desktop, ou Docker installé dans WSL : lancer alors les commandes `docker` depuis WSL, dans le
dossier du dépôt, par exemple `/mnt/c/Users/.../Ingeco`).

### Base de données (MySQL dans Docker)

Un conteneur MySQL 8.4 local, décrit dans `compose.yaml`. Au premier démarrage, il crée la base
avec `sql/schema-mvp.sql` (schéma et données de référence), puis `sql/demo-data.sql` (comptes et
courses de test). Ce second script ne doit **jamais** être chargé ailleurs que sur un poste de
développement : ses comptes ont un mot de passe public, dont un administrateur.

```bash
cp .env.example .env               # puis remplacer les deux mots de passe
docker compose up -d               # démarre la base sur 127.0.0.1:3307
docker compose ps                  # « healthy » quand elle est prête
```

Les scripts ne sont relus que si la base est vide. Après une modification de `sql/` :

```bash
docker compose down -v             # EFFACE la base
docker compose up -d               # la recrée avec le script
```

Pour ouvrir une console SQL : `docker compose exec db mysql -u enroute -p enroute`.

### Back-end

```bash
cd BACKEND
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # sous Linux/macOS : .venv/bin/python
cp .env.example .env
```

Dans `.env`, remplacer `FLASK_SECRET_KEY` par une clé générée avec :

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Facultatif : pour chercher de vraies adresses et calculer la vraie distance par la route, créer un
compte gratuit sur [OpenRouteService](https://openrouteservice.org) et copier sa clé dans
`ORS_API_KEY`. Sans clé, l'API utilise une douzaine de lieux publics factices de la zone du pilote
(mairies, gare routière, aéroport…) et une distance estimée, sans appel à Internet. Les tests
n'appellent jamais OpenRouteService, même avec une clé.

Puis :

```bash
.venv/Scripts/python -m app        # lance l'API sur http://localhost:5000
.venv/Scripts/python -m pytest     # lance les tests
```

### Front-end

```bash
cd FRONTEND
npm install
cp .env.example .env
npm run dev                        # lance l'interface sur http://localhost:5173
```

La page http://localhost:5173/diagnostic indique si l'interface joint bien l'API et la base.

### Comptes de test

Pour l'instant, l'API lit encore les comptes dans des **données factices en mémoire**
(`BACKEND/app/repository/user_repository.py`), chargées seulement avec `LOAD_DEMO_DATA=true` dans
`BACKEND/.env` (c'est la valeur de `.env.example`) : elles reviennent à cet état à chaque
redémarrage de l'API. Sans ce réglage, l'API démarre sans aucun compte. Elle refuse de démarrer
avec ce réglage si `COOKIE_SECURE=true` (serveur en https, donc hébergé). Les mêmes comptes sont
dans `sql/demo-data.sql`, sauf David (référent partenaire), qui est dans
`sql/schema-hors-scope.sql` avec les bons solidaires. Personnes fictives, mot de passe commun
**`Trajet-2026!`**.

**Inscription d'un nouvel usager** : les SMS sont simulés. Avec `LOAD_DEMO_DATA=true`, le code
reçu par SMS est toujours **`123456`** ; sans, il est tiré au hasard et n'est écrit nulle part.

| Téléphone | Prénom | Rôle |
|---|---|---|
| 0694 00 00 01 | Alice | Usager |
| 0694 00 00 02 | Bruno | Usager prioritaire, besoin d'un véhicule adapté |
| 0694 00 00 03 | Chloé | Chauffeur |
| 0694 00 00 04 | David | Référent partenaire |
| 0694 00 00 05 | Emma | Opérateur (centre d'appel) |
| 0694 00 00 06 | Farid | Administrateur : « Comptes » sur l'accueil pour créer un chauffeur, suspendre, générer un code |
| 0694 00 00 07 | Gaëlle | Usager créé par le centre d'appel, **à activer** avec le code `12345678` (« J'ai reçu un code ») |
| 0694 00 00 08 | Hugo | Usager suspendu |

Alice a aussi quatre trajets passés, factices eux aussi (`BACKEND/app/repository/ride_repository.py`) :
trois terminés, dont un déjà noté, et un annulé. Ils servent à essayer « Mes trajets » et la
notation sans passer par le côté chauffeur. Les tests partent sans aucun trajet.

Pour essayer une course de bout en bout : réserver et payer un trajet en Alice, se déconnecter,
puis se connecter en Chloé, appuyer sur « Je suis disponible » et ouvrir « Courses ». Sans
position autorisée, Chloé voit les courses de toute la zone. Ses revenus sont dans « Mes
revenus », sur son accueil : les trajets factices d'Alice comptent comme les siens.

En développement, `COOKIE_SECURE=false` dans `BACKEND/.env` : les cookies de session marqués
`Secure` ne passent qu'en HTTPS, ce qui bloque Safari sur `http://localhost` et tout téléphone qui
teste l'appli par l'adresse IP de l'ordinateur. Une fois déployé, toujours `true` (HTTPS).

---

## 5. Pour l'équipe base de données

Cette partie s'adresse aux trois membres de l'équipe BD. Elle explique comment l'API se
connectera à votre base, et ce dont les développeurs ont besoin de votre part.

**Pour concevoir le schéma, partir de [docs/contrat-api.md](docs/contrat-api.md)** : il liste
les données que l'API devra lire et écrire, route par route.

### Le principe : le dossier `sql/` est à vous

- **Tout ce qui est dans `sql/` est à vous** : le schéma, les migrations, les données de
  référence, les données de test, les index et les vues. Les développeurs n'y touchent plus
  (décidé le 03/11/2026).
- **Les développeurs ne créent ni ne modifient jamais une table.** Le code de l'API se contente
  de lire et d'écrire dans les tables que vous avez créées.
- Si une fonctionnalité demande une nouvelle table ou une nouvelle colonne, les développeurs
  vous envoient une **demande écrite** (une issue GitHub, voir plus bas). C'est vous qui décidez
  et qui écrivez la migration.
- Ces fichiers SQL font partie du **rendu noté de la SAÉ**, et c'est vous qui les présentez à la
  soutenance.

### Qui fait quoi

| Sujet | Équipe BD | Développeurs |
|---|---|---|
| Schéma (`sql/schema-mvp.sql`, `sql/schema-hors-scope.sql`) | Écrit, relu, validé | Lisent ; demandent un changement par écrit |
| Migrations (`sql/migrations/`) | Écrites et appliquées | Jamais |
| Données de référence (communes, tarif, types de trajets…) | Écrites | Demandent une valeur si besoin |
| Données de test (`sql/demo-data.sql`) | Écrites et tenues à jour, personnes fictives | Demandent les comptes dont ils ont besoin pour tester |
| Index et contraintes | Écrits (à partir de [contrat-api.md](docs/contrat-api.md), partie 6.6) | Signalent une requête lente |
| Requêtes lourdes (statistiques, chauffeurs proches, consommation des bons) | Écrites, en **vues SQL** (voir plus bas) | Lisent la vue depuis `repository/` |
| Requêtes courantes (lire un compte, créer une course…) | Relisent si elles le souhaitent | Écrites en Python (SQLAlchemy) dans `repository/` |
| Classes Python qui décrivent vos tables (`BACKEND/app/models/`) | – | Écrites, en suivant exactement votre schéma |
| Chargement de la base locale (partie base de `compose.yaml`) | Ajoutent les lignes de leurs fichiers | Ne la changent pas sans vous |

### Les migrations

Tant que personne n'a de vraies données, on peut effacer la base et la recréer
(`docker compose down -v`). Dès la mise en service de janvier 2027, ce ne sera plus possible :
une base en production se **modifie**, elle ne se recrée pas. Les migrations servent à ça.

- **Le point de départ** : `sql/schema-mvp.sql`, tel que vous l'aurez relu et validé (version 2).
  Une fois validé, **on ne le modifie plus**.
- **Chaque changement ensuite** est un nouveau fichier dans `sql/migrations/`, numéroté sur trois
  chiffres, avec un nom qui dit ce qu'il fait :

  ```
  sql/migrations/
    001_ajouter_version_session.sql
    002_creer_bon_solidaire.sql
    003_creer_vue_stats_trajets.sql
  ```

- **Un fichier déjà mergé ne se modifie jamais.** Une erreur se corrige par une nouvelle
  migration. Sinon, deux bases qui ont appliqué deux versions du même fichier ne sont plus
  pareilles.
- **Un changement par fichier**, en SQL MySQL pur, appliqué dans l'ordre des numéros.
- **En tête de chaque fichier**, en commentaire : la date, l'auteur, la demande liée (numéro
  d'issue), et comment revenir en arrière.

  ```sql
  -- 001 : colonne version_session sur utilisateur
  -- 05/11/2026, équipe BD, issue #NN (audit de sécurité, F3)
  -- Retour arrière : ALTER TABLE utilisateur DROP COLUMN version_session;
  ALTER TABLE utilisateur ADD COLUMN version_session INT NOT NULL DEFAULT 0;
  ```

- **En local**, la base doit se créer avec : le schéma, puis toutes les migrations dans l'ordre,
  puis les données de test. Pour la première migration, ajoutez ce chargement dans `compose.yaml`
  (les fichiers de `docker-entrypoint-initdb.d` s'exécutent par ordre alphabétique, et les
  données de test doivent passer en dernier). Prévenez les développeurs : ils devront refaire
  `docker compose down -v` puis `up -d`.
- Les développeurs suivent chaque migration dans leurs classes Python (`models/`). Annoncez-la
  avant de la merger.

### Les requêtes SQL

L'API écrit elle-même ses requêtes courantes, en Python (SQLAlchemy, voir plus bas). Ce qui vous
revient, ce sont les **requêtes lourdes**, celles qui demandent de bien connaître le SGBD :

| Requête | Pour | Quand |
|---|---|---|
| Statistiques : trajets par jour, par commune, par motif, note moyenne, taux de satisfaction (notes de 4 ou 5) | Tableau de bord administrateur (UC56) | Sprint 3 (02/12 → 10/12) |
| Chauffeurs en ligne les plus proches d'un point | Proposer une course (contrat 6.1) | Quand vous le pouvez ; l'API a une version simple en attendant |
| Consommation des bons par structure | Suivi des référents (contrat 6.4) | Avec les tables des bons |

**Livrez-les sous forme de vues** (`CREATE VIEW`), chacune dans une migration. L'API lit une vue
comme une table : votre requête reste à un seul endroit, dans vos fichiers, et vous pouvez la
tester directement dans MySQL. Les tests automatiques de l'API tournent sur SQLite : écrivez les
vues en SQL standard quand c'est possible, et signalez ce qui est propre à MySQL.

### La base locale : MySQL 8.4 dans Docker

En local, l'API est branchée sur un conteneur **MySQL 8.4** (`compose.yaml`, voir la
[partie 4](#4-lancer-le-projet)), créé à partir de `sql/schema-mvp.sql`. Ce script est la version 2
du schéma, réécrite d'après le [contrat d'API](docs/contrat-api.md) ; `sql/schema-hors-scope.sql`
garde ce qui n'est pas encore dans le périmètre (bons solidaires, documents, formation).

Les tests automatiques (`pytest`, CI) tournent encore sur SQLite en mémoire : ils ne lisent pas
la base. Le déploiement (hébergement de la base) sera choisi en fin de projet.

### Comment l'API parle à la base : SQLAlchemy

L'API utilise **SQLAlchemy**, une bibliothèque Python qui sait parler à la plupart des SGBD.
Le code de l'API décrit les requêtes en Python, et SQLAlchemy les traduit dans le SQL de votre
SGBD. Par exemple, cette ligne :

```python
select(Ride).where(Ride.status == "pending").limit(10)
```

devient `SELECT ... FROM ride WHERE status = 'pending' LIMIT 10` sous PostgreSQL ou MySQL, et
la syntaxe équivalente sous SQL Server ou Oracle.

Conséquence pour vous : **changer de SGBD ne demande presque aucune modification du code.** Il
suffit de changer une ligne de configuration et d'installer le pilote correspondant.

Pour chaque table que vous créez, les développeurs écrivent une classe Python qui la décrit,
colonne par colonne (dans `BACKEND/app/models/`). Cette classe **décrit** votre table, elle ne
la crée pas.

### Brancher votre base sur l'API

La connexion se règle dans le fichier `BACKEND/.env`, à la ligne `DATABASE_URL`. Le format
dépend du SGBD :

| SGBD | `DATABASE_URL` | Pilote Python à ajouter dans `requirements.txt` |
|---|---|---|
| MySQL (actuel) | `mysql+pymysql://utilisateur:motdepasse@127.0.0.1:3307/nom_base?charset=utf8mb4` | `PyMySQL` et `cryptography` (déjà installés) |
| SQLite (tests) | `sqlite://` | Aucun (inclus dans Python) |
| PostgreSQL | `postgresql+psycopg://utilisateur:motdepasse@hote:5432/nom_base` | `psycopg[binary]` |
| SQL Server | `mssql+pyodbc://utilisateur:motdepasse@hote:1433/nom_base?driver=ODBC+Driver+18+for+SQL+Server` | `pyodbc` (+ pilote ODBC de Microsoft) |
| Oracle | `oracle+oracledb://utilisateur:motdepasse@hote:1521/?service_name=nom_service` | `oracledb` |

Le fichier `.env` n'est jamais envoyé sur GitHub : les mots de passe qu'il contient restent
sur votre machine.

### Vérifier que la connexion marche

1. Lancer l'API (voir la [partie 4](#4-lancer-le-projet)).
2. Ouvrir http://localhost:5000/health dans le navigateur.

Si tout va bien, la réponse indique le SGBD utilisé :

```json
{ "status": "ok", "database": { "reachable": true, "dialect": "postgresql" } }
```

Si la base ne répond pas : `"status": "degraded"` et `"reachable": false`. Le détail de l'erreur
(mauvais mot de passe, mauvais port…) s'affiche dans le terminal où tourne l'API.

### Ce dont les développeurs ont besoin de votre part

Dans l'ordre, avec la date à laquelle on en a besoin (calendrier dans
[docs/questions-sprint-2026-11-04.md](docs/questions-sprint-2026-11-04.md)) :

1. **Confirmer le SGBD** : MySQL 8.4, celui de votre première version. Le pilote Python et
   quelques requêtes en dépendent.
2. **Relire et valider le schéma** (`sql/schema-mvp.sql`), **pour le 17/11** : l'API se branche
   sur MySQL au sprint 2 (18/11 → 01/12). Votre première version avait été écrite avant le
   contrat d'API v2 : les développeurs l'ont réécrite (version 2) pour qu'elle couvre le contrat,
   en gardant vos choix (MySQL, noms en français, identifiants entiers). C'était la dernière fois
   qu'ils touchaient à `sql/` : à vous de le corriger et de le valider. Une fois validé, il devient
   le point de départ des migrations. Le script fait foi : les classes Python suivent le script,
   pas l'inverse.
3. **Première migration** : la colonne `version_session` (voir « Demandes de l'audit » plus
   bas).
4. **Où stocker la photo du chauffeur** : en base (binaire) ou en fichier sur le serveur, avec sa
   référence en base ([contrat-api.md](docs/contrat-api.md), H19).
5. **Les vues des statistiques**, pour le sprint 3 (voir « Les requêtes SQL »).
6. **Les tables des bons solidaires**, dès que la cliente aura dit comment marche un bon (point
   de départ : `sql/schema-hors-scope.sql`).
7. **Où héberger la base en production**, pour la mise en service de janvier.
8. **Votre partie du rapport de gestion et de la soutenance** : le temps passé par chacun, et qui
   présente quoi sur la base.

Et en continu : les **données de référence** (communes desservies : Cayenne, Rémire-Montjoly et
Matoury pour le pilote ; types de trajets, profils…) et les **données de test**, toujours
fictives. Le RGPD interdit toute donnée personnelle réelle : faux noms, faux téléphones, fausses
adresses.

### Demander un changement de schéma

Les développeurs ouvrent une **issue GitHub** avec l'étiquette `bd`, qui dit :

- le besoin, en une phrase, et la fonctionnalité concernée (cas d'utilisation, route) ;
- la table ou la colonne proposée (nom, type, contraintes), comme simple suggestion ;
- la date à laquelle l'API en a besoin.

Vous répondez dans l'issue (accord, autre forme, question), puis vous livrez la migration par une
pull request qui cite l'issue. Un développeur relit la pull request, pour vérifier que l'API
pourra s'en servir ; vous relisez de même les classes Python qui décrivent vos tables, si vous le
souhaitez.

### Demandes de l'audit de sécurité (02/11/2026)

L'[audit](docs/audit-securite-2026-11-02.md) demande deux changements de schéma. Les développeurs
ne les appliquent pas : à vous de les reprendre (la colonne, dans une migration), ou d'en proposer
une autre forme.

1. **Une colonne `version_session`** (entier, `NOT NULL DEFAULT 0`) sur `utilisateur`. L'API
   l'augmente à chaque nouveau mot de passe et à chaque suspension, et la relit à chaque requête
   (par la clé primaire) : les sessions ouvertes avant prennent fin. Elle vit pour l'instant dans
   les données factices de l'API.
2. **Les données de test sont séparées du schéma** : `sql/demo-data.sql`, chargé en local par
   `compose.yaml` après `sql/schema-mvp.sql`. Merci de garder cette séparation dans vos versions :
   un environnement hébergé ne charge que le schéma et les données de référence.

Les inscriptions en attente de leur code SMS restent en mémoire de l'API (10 minutes au plus) :
aucune table n'est demandée pour elles tant que l'API ne tourne que dans un processus.

### Ce qui nous aiderait (suggestions, pas des obligations)

- **Des noms de tables et de colonnes en minuscules avec des underscores** (`bon_solidaire`,
  `date_reservation`). Ils se lisent directement en Python, et ne posent pas de problème de
  majuscules d'un SGBD à l'autre.
- **Des contraintes en base** (clés étrangères, `NOT NULL`, `CHECK`, unicité) : elles protègent
  les données même si l'API a un bug.
- **Penser à la géolocalisation.** L'application doit trouver le chauffeur disponible le plus
  proche et suivre les trajets sur une carte. Selon le SGBD, il existe des extensions dédiées
  (PostGIS pour PostgreSQL, types spatiaux pour MySQL ou SQL Server) qui facilitent ces calculs.
- **La traçabilité des trajets financés** par un partenaire est exigée par le cahier des charges :
  qui a financé quel trajet, avec quel bon, et quand.

### Une question, un changement ?

Pour toute question sur l'utilisation de la base par l'API, ou toute demande de modification
du schéma, passer par une issue GitHub ou contacter directement les développeurs. Un changement
de schéma déjà livré doit être annoncé : l'API devra suivre.

---

## 6. Règles de travail

- Pas de push direct sur `main` : une branche par fonctionnalité (`feature/...`, `fix/...`, `perf/...`) et une
  pull request relue par l'autre développeur.
- **Intégration continue** (GitHub Actions, `.github/workflows/ci.yml`) : chaque pull request
  lance les tests du back (`pytest`), le lint et le build du front, et vérifie que les types de
  l'API du front sont à jour (`npm run api:types`). Elle cherche aussi les failles connues des
  dépendances (`pip-audit`, `npm audit --omit=dev`) et les secrets commités (Gitleaks, valeurs de
  test publiques listées dans `.gitleaks.toml`). **Une pull request ne peut être mergée que si
  tout passe.**
- Messages de commit courts, à l'impératif, préfixés : `feat:`, `fix:`, `perf:`, `docs:`, `refactor:`,
  `test:`, `chore:`.
- Les secrets (mots de passe, clés) vont dans les fichiers `.env`, jamais sur GitHub.
- Aucune donnée personnelle réelle dans les tests, les données d'exemple ou les logs (RGPD).
