# Développer sur le projet

Pour les développeurs. Pour simplement lancer l'application, le [README](../README.md) suffit.
L'organisation du code et ses règles sont dans [architecture.md](architecture.md), le pourquoi de
chaque choix technique dans les [fiches de décision](adr/README.md).

## Sommaire

- [Technologies](#technologies)
- [Organisation du dépôt](#organisation-du-dépôt)
- [Ports utilisés](#ports-utilisés)
- [Base de données (MySQL dans Docker)](#base-de-données-mysql-dans-docker)
- [Back-end](#back-end)
- [Front-end](#front-end)
- [Comptes de test : détails](#comptes-de-test--détails)
- [Règles de travail](#règles-de-travail)

## Technologies

| Partie | Technologies |
|---|---|
| Back-end (API) | Python 3.14, Flask, Flask-SocketIO (temps réel), SQLAlchemy (accès à la base), Pydantic (validation), Flask-JWT-Extended (connexion) |
| Front-end | React 19, TypeScript, Vite, application web installable sur mobile (PWA) |
| Base de données | **MySQL 8.4**, en local dans Docker (choix de l'équipe BD, confirmé le 03/11/2026) |
| Documentation de l'API | Générée automatiquement (Swagger) : http://localhost:5000/apidoc/swagger |

Prérequis pour développer : **Python 3.14**, **Node.js 24**, et **Docker** pour la base (Docker
Desktop, ou Docker installé dans WSL : lancer alors les commandes `docker` depuis WSL, dans le
dossier du dépôt, par exemple `/mnt/c/Users/.../Ingeco`).

## Organisation du dépôt

```
BACKEND/      L'API en Python
  app/
    controllers/   Reçoit les requêtes HTTP
    services/      Les règles métier
    repository/    Le SEUL endroit qui parle à la base de données
    models/        La description en Python des tables de l'équipe BD
  tests/
FRONTEND/     L'interface web (React)
sql/          Scripts de la base (équipe BD) : schéma, migrations, données de test
docs/         Cahier des charges, architecture, décisions
compose.yaml  Base, API et interface en local (Docker)
```

## Ports utilisés

Tous les ports ne sont ouverts que sur cet ordinateur (`127.0.0.1`), jamais sur le réseau.

| Port | Service | Lancé par | Réglage |
|---|---|---|---|
| **5173** | Interface, http://localhost:5173 | `docker compose up -d` (service `web`) ou `npm run dev` | – |
| **5000** | API, Swagger sur `/apidoc/swagger` | `docker compose up -d` (service `api`) ou `python -m app` | `PORT` dans `BACKEND/.env` |
| **3307** | Base MySQL de développement | `docker compose up -d` (service `db`) | `MYSQL_PORT` dans `.env` |
| **8081** | Adminer, la base dans le navigateur | `docker compose --profile outils up -d adminer` | `ADMINER_PORT` dans `.env` |
| **3308** | Base MySQL des tests, jetable | `docker compose --profile test up -d db-test` | – |

Le mode démo (tout en Docker) et le mode développement (`python -m app`, `npm run dev`) se
disputent les ports 5000 et 5173 : arrêter l'un avant de lancer l'autre
(`docker compose stop api web`).

`docker compose up -d --build` lance tout, comme dans le README. C'est un **mode démo** : comptes
au mot de passe public, cookies sur `http`, interface compilée (une modification du code ne
s'affiche qu'après un nouveau `--build`). Pour développer, lancer la base seule, puis l'API et
l'interface à la main (ci-dessous).

## Base de données (MySQL dans Docker)

Un conteneur MySQL 8.4, décrit dans `compose.yaml`. Au premier démarrage, `sql/charger-base.sh`
charge `sql/schema-mvp.sql`, puis les migrations de `sql/migrations/` dans l'ordre, puis
`sql/demo-data.sql` (comptes et courses de test). Ce dernier ne se charge **jamais** ailleurs que
sur un poste de développement : ses comptes ont un mot de passe public, dont un administrateur.

```bash
cp .env.example .env               # puis remplacer les deux mots de passe et FLASK_SECRET_KEY
docker compose up -d db            # la base seule, sur 127.0.0.1:3307
docker compose ps                  # « healthy » quand elle est prête
```

- **Une nouvelle migration est arrivée** : rien à effacer. `docker compose up -d` lance le service
  `db-migrate`, qui applique les migrations que la base n'a pas encore reçues, puis s'arrête.
  Base seule : `docker compose up -d db db-migrate`, puis `docker compose logs db-migrate`.
- **Remettre la démo à zéro** : la commande du [README](../README.md#remettre-la-démo-à-zéro).
- **Tout effacer** et recréer la base : `docker compose down -v`, puis `docker compose up -d db`.
- **Console SQL** : `docker compose exec db mysql -u enroute -p enroute`.
- **Consulter la base dans le navigateur** avec Adminer ([ADR 021](adr/021-adminer.md)), jamais
  pendant une démo : `docker compose --profile outils up -d adminer`, puis http://localhost:8081
  (système MySQL, serveur `db`, utilisateur `enroute`, mot de passe `MYSQL_PASSWORD` du `.env`,
  base `enroute`). L'arrêter avec `docker compose stop adminer`. Une donnée modifiée à la main se
  défait en remettant la démo à zéro ; le schéma ne se change jamais par là.

Migrations, export par `mysqldump` et partage du travail avec l'équipe BD :
[guide-equipe-bd.md](guide-equipe-bd.md).

## Back-end

```bash
cd BACKEND
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # sous Linux/macOS : .venv/bin/python
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"   # à copier dans FLASK_SECRET_KEY
.venv/Scripts/python -m app        # l'API sur http://localhost:5000
```

La base doit être lancée avant l'API (`docker compose up -d db`).

Facultatif : pour de vraies adresses et la vraie distance par la route, copier une clé
[OpenRouteService](https://openrouteservice.org) dans `ORS_API_KEY` (compte au nom de la
structure : [comptes-externes.md](comptes-externes.md)). Sans clé, l'API utilise une douzaine de
lieux fictifs de la zone du pilote et une distance estimée, sans appel à Internet. Les tests
n'appellent jamais OpenRouteService.

Les tests tournent sur une base MySQL à part, jetable (jamais celle de développement), recréée
depuis `sql/` à chaque lancement :

```bash
docker compose --profile test up -d db-test   # depuis la racine, une fois
cd BACKEND && .venv/Scripts/python -m pytest
```

## Front-end

```bash
cd FRONTEND
npm install
cp .env.example .env
npm run dev                        # l'interface sur http://localhost:5173
```

La page http://localhost:5173/diagnostic indique si l'interface joint bien l'API et la base.
Les autres commandes (`lint`, `lint:texts`, `test`, `build`, `api:types`) sont listées dans
[CLAUDE.md](../CLAUDE.md#commandes).

## Comptes de test : détails

La liste courte est dans le [README](../README.md#comptes-de-test). Tous les comptes et toutes les
courses de test viennent de `sql/demo-data.sql` ; l'API n'en crée aucun elle-même.

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
| 0694 00 00 09 | Inès | Chauffeur, véhicule non adapté |

- **Codes SMS fixes** (`123456` à l'inscription, `12345678` pour un mot de passe oublié) :
  seulement avec `LOAD_DEMO_DATA=true` dans `BACKEND/.env` (valeur de `.env.example`). Sans, ils
  sont tirés au hasard et écrits nulle part. Le code de mot de passe oublié marche pour tous les
  comptes sauf Farid et Hugo. L'API refuse de démarrer avec `LOAD_DEMO_DATA=true` si
  `COOKIE_SECURE=true` (serveur en https, donc hébergé).
- **Trajets de test**, datés par rapport au chargement : Alice en a six (trois terminés avec
  Chloé dont le plus ancien déjà noté, un annulé, un expiré, et un programmé dans trois jours qui
  attend son paiement et expire au bout de 15 minutes). Bruno a un trajet programmé dans deux
  jours, réservé par Emma, qui attend un chauffeur.
- **Une course de bout en bout** : réserver un trajet en Alice, puis se connecter en Chloé
  (fenêtre privée), « Je suis disponible », puis « Courses ». Sans position autorisée, Chloé voit
  les courses de toute la zone. Ses revenus sont dans « Mes revenus ».
- **`COOKIE_SECURE=false`** en développement : les cookies `Secure` ne passent qu'en HTTPS, ce qui
  bloquerait Safari sur `http://localhost` et un téléphone qui teste par l'adresse IP de
  l'ordinateur. Une fois déployé, toujours `true`.

## Règles de travail

- Pas de push direct sur `main` : une branche par fonctionnalité (`feature/...`, `fix/...`,
  `perf/...`, `docs/...`) et une pull request relue par l'autre développeur.
- **Intégration continue** (`.github/workflows/ci.yml`) : chaque pull request lance `pytest`, le
  lint, les tests et le build du front, vérifie que les types de l'API sont à jour
  (`npm run api:types`), cherche les failles connues des dépendances (`pip-audit`,
  `npm audit --omit=dev`) et les secrets commités (Gitleaks). **On ne merge que si tout passe.**
- Messages de commit courts, à l'impératif, préfixés : `feat:`, `fix:`, `perf:`, `docs:`,
  `refactor:`, `test:`, `chore:`.
- Les secrets vont dans les fichiers `.env`, jamais sur GitHub.
- Aucune donnée personnelle réelle dans les tests, les données d'exemple ou les logs (RGPD).
