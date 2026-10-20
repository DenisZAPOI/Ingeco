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
avec `sql/schema-mvp.sql` (schéma et données de test).

```bash
cp .env.example .env               # puis remplacer les deux mots de passe
docker compose up -d               # démarre la base sur 127.0.0.1:3307
docker compose ps                  # « healthy » quand elle est prête
```

Le script n'est relu que si la base est vide. Après une modification de `sql/schema-mvp.sql` :

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
(`BACKEND/app/repository/user_repository.py`) : ils reviennent à cet état à chaque redémarrage de
l'API. Les mêmes comptes sont dans les données de test de `sql/schema-mvp.sql`, sauf David
(référent partenaire), qui est dans `sql/schema-hors-scope.sql` avec les bons solidaires. Personnes
fictives, mot de passe commun **`Trajet-2026!`**.

| Téléphone | Prénom | Rôle |
|---|---|---|
| 0694 00 00 01 | Alice | Usager |
| 0694 00 00 02 | Bruno | Usager prioritaire, besoin d'un véhicule adapté |
| 0694 00 00 03 | Chloé | Chauffeur |
| 0694 00 00 04 | David | Référent partenaire |
| 0694 00 00 05 | Emma | Opérateur (centre d'appel) |
| 0694 00 00 06 | Farid | Administrateur |
| 0694 00 00 07 | Gaëlle | Usager créé par le centre d'appel, **à activer** avec le code `12345678` (« J'ai reçu un code ») |
| 0694 00 00 08 | Hugo | Usager suspendu |

En développement, `COOKIE_SECURE=false` dans `BACKEND/.env` : les cookies de session marqués
`Secure` ne passent qu'en HTTPS, ce qui bloque Safari sur `http://localhost` et tout téléphone qui
teste l'appli par l'adresse IP de l'ordinateur. Une fois déployé, toujours `true` (HTTPS).

---

## 5. Pour l'équipe base de données

Cette partie s'adresse aux trois membres de l'équipe BD. Elle explique comment l'API se
connectera à votre base, et ce dont les développeurs ont besoin de votre part.

**Pour concevoir le schéma, partir de [docs/contrat-api.md](docs/contrat-api.md)** : il liste
les données que l'API devra lire et écrire, route par route.

### Le principe : la base est à vous

- **Vous choisissez le SGBD** (PostgreSQL, MySQL, MariaDB, SQL Server, Oracle…), vous concevez
  le schéma, vous écrivez les scripts de création et les données de référence.
- **Les développeurs ne créent ni ne modifient jamais une table.** Le code de l'API se contente
  de lire et d'écrire dans les tables que vous avez créées.
- Si une fonctionnalité demande une nouvelle table ou une nouvelle colonne, les développeurs
  vous envoient une **demande écrite**. C'est vous qui décidez et qui modifiez le schéma.

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

1. **Confirmer le SGBD** : MySQL 8.4, celui de votre première version. Le pilote Python et
   quelques requêtes en dépendent.
2. **Relire le script de création du schéma** du dossier `sql/`. Votre première version avait
   été écrite avant le contrat d'API v2 : les développeurs l'ont réécrite (version 2) pour
   qu'elle couvre le contrat, en gardant vos choix (MySQL, noms en français, identifiants
   entiers). Le script fait foi : les classes Python suivent le script, pas l'inverse. Toute
   correction passe par une pull request sur `sql/`.
3. **Les données de référence** (communes desservies : Cayenne, Rémire-Montjoly et Matoury pour
   le pilote ; types de trajets, profils…), et des **données de test
   fictives**. Le RGPD interdit toute donnée personnelle réelle : faux noms, faux téléphones,
   fausses adresses.
4. **La date de livraison**, même approximative, pour organiser le travail.
5. **Comment se connecter** : pour le développement, une base locale sur chaque machine, dans
   Docker (`compose.yaml`, voir la [partie 4](#4-lancer-le-projet)). L'hébergement de la base
   en production sera choisi en fin de projet.

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
  l'API du front sont à jour (`npm run api:types`). **Une pull request ne peut être mergée que si
  les trois passent.**
- Messages de commit courts, à l'impératif, préfixés : `feat:`, `fix:`, `perf:`, `docs:`, `refactor:`,
  `test:`, `chore:`.
- Les secrets (mots de passe, clés) vont dans les fichiers `.env`, jamais sur GitHub.
- Aucune donnée personnelle réelle dans les tests, les données d'exemple ou les logs (RGPD).
