# Architecture

Ce document explique **comment le code est rangé et pourquoi**. À lire avant d'écrire la
première route ou le premier écran. Le modèle est le socle de ProjectOrganizer (R5.A.05),
adapté au projet.

---

## 1. Back-end (`BACKEND/`)

### Technologies

| Rôle | Bibliothèque | Version |
|---|---|---|
| Serveur web | Flask | 3.1.3 |
| Temps réel | Flask-SocketIO (+ simple-websocket en dev) | 5.6.1 |
| Appels depuis le front | Flask-Cors | 6.0.5 |
| Accès à la base | SQLAlchemy | 2.0.54 |
| Validation et documentation d'API | Pydantic + flask-pydantic-spec | 2.13.5 / 0.8.7 |
| Authentification (JWT en cookies) | Flask-JWT-Extended | 4.7.4 |
| Configuration | python-dotenv | 1.2.2 |
| Tests | pytest | 9.1.1 |

Versions figées dans `requirements.txt`. Le pilote de la base (PostgreSQL, MySQL…) sera ajouté
quand l'équipe BD aura choisi son SGBD. D'ici là : SQLite en local, base vide.

### Dossiers

```
BACKEND/
├── requirements.txt / pytest.ini / .env.example
├── tests/                      conftest.py, test_foundation.py (le socle), un fichier par ressource
└── app/
    ├── __main__.py             Lancement : python -m app
    ├── main.py                 Fabrique create_app() : montage de tout le reste
    ├── config.py               Lecture du .env (échoue au démarrage si une variable manque)
    ├── extensions.py           socketio, spec (documentation OpenAPI)
    ├── controllers/            HTTP ↔ services                 modèle : health_controller.py
    ├── dtos/                   Modèles Pydantic entrée/sortie   modèle : health_dto.py (base.py)
    ├── services/               Règles métier                    modèle : health_service.py
    ├── repository/             Seul accès à la base             modèle : health_repository.py
    ├── models/                 Modèles ORM des tables de l'équipe BD (vide pour l'instant)
    ├── sockets/                Événements temps réel ; broadcast.py pour émettre
    └── utils/                  database, errors, logs, request_logs, security_headers,
                                access (session, rôles), passwords, rate_limit
```

Chaque dossier de couche a un `__init__.py` qui rappelle ce qu'on y range. **`GET /health` est
la seule fonctionnalité du socle** : elle traverse toutes les couches jusqu'à la base et sert
d'exemple à recopier.

| Dossier | Contient | Ne contient **jamais** |
|---|---|---|
| `controllers/` | Un Blueprint par ressource : lit la requête, appelle un service, renvoie le DTO | Règle métier, SQL |
| `dtos/` | Schémas d'entrée (`InputModel`) et de sortie (`ApiModel`) | Logique |
| `services/` | Qui a le droit, quelle transition d'état est permise, la transaction | `request`, `jsonify`, codes HTTP |
| `repository/` | Lectures et écritures en base (ou données factices tant que le schéma n'est pas livré) | Règle métier, erreur HTTP |
| `models/` | Correspondance classes Python ↔ tables **existantes** | Logique, création de table |
| `sockets/` | Réception et émission des événements | Règle métier : il appelle les services |

### Règle de dépendance

```
controllers/ ─┐
sockets/     ─┴─▶ services/ ──▶ repository/ ──▶ models/
                      └──▶ utils/ (accessible à tous)
```

Un service n'importe jamais Flask ; un repository ne lève jamais d'erreur HTTP ; un contrôleur
n'écrit jamais de SQL. Les services se testent donc sans serveur, et le canal WebSocket réutilise
exactement les mêmes règles que les routes HTTP.

### Base de données

- La base appartient à l'équipe BD. On n'appelle **jamais** `Base.metadata.create_all()` et on ne
  crée ni ne modifie aucune table. Un besoin de schéma → une demande écrite à l'équipe BD.
- Approche mixte : une ligne d'ORM lisible → ORM ; trois jointures ou une condition fine → SQL
  explicite dans `repository/`.
- Toute écriture passe par `database.session()`, qui valide à la sortie du bloc et annule en cas
  d'erreur. Une opération en plusieurs étapes (réserver et consommer un bon) tient dans **une**
  transaction.

### Contrat d'API

- JSON en **camelCase**, Python en snake_case : la traduction est faite par `dtos/base.py`, nulle
  part ailleurs.
- Un champ sans valeur est envoyé à `null`, jamais omis (les types du front l'attendent).
- Un champ inconnu dans un corps de requête → 400.
- Format unique des erreurs : `{ "error": "...", "detail": ... }`. Un service lève une erreur de
  `utils/errors.py`, le gestionnaire la traduit.

| Code | Situation |
|---|---|
| 400 | Charge invalide (`detail.fields` liste les champs fautifs) |
| 401 | Pas de jeton, jeton expiré ou invalide |
| 403 | Rôle insuffisant pour cette action |
| 404 | Ressource inexistante ou invisible pour l'appelant |
| 409 | Conflit avec l'état (course déjà acceptée) |
| 422 | Règle métier violée (bon épuisé) |
| 429 | Trop d'essais ratés (connexion, code d'activation) |

- Le `detail` d'une erreur métier est affiché tel quel à l'usager : **en français**, en mots simples.
  Les messages de validation de Pydantic sont traduits dans `utils/errors.py` ; une règle écrite
  dans `services/` lève `ValueError` avec son message, transformé en erreur de champ par
  `apply_rule` (`dtos/base.py`).
- Documentation générée depuis les DTOs : http://localhost:5000/apidoc/swagger. Chaque route
  déclare **tous** ses codes d'erreur dans `@spec.validate(resp=Response(...))`, avec `ErrorDto`.
  Une réponse non conforme à son DTO renvoie 500 : c'est un bug à corriger.

### Authentification

- **Session** : deux JWT dans des cookies `HttpOnly`, posés par Flask-JWT-Extended. Jeton d'accès
  de 15 minutes, jeton de renouvellement de 30 jours limité au chemin `/auth/refresh`. Cookies
  `SameSite=Lax`, `Secure` sauf si `COOKIE_SECURE=false` (développement en http).
- **CSRF** : double envoi. L'API pose aussi des cookies lisibles (`csrf_access_token`,
  `csrf_refresh_token`) ; `api/client.ts` les recopie dans l'en-tête `X-CSRF-TOKEN` de chaque
  écriture. Un site tiers ne peut pas lire ces cookies, donc pas forger la requête.
- **Renouvellement** : sur un `401`, `api/client.ts` appelle une fois `POST /auth/refresh`, puis
  rejoue l'appel. Le renouvellement relit le compte : un compte suspendu perd l'accès en 15 minutes
  au plus.
- **Rôles** : `@require_login("admin", ...)` dans le contrôleur, **au-dessus** de `@spec.validate`.
  Sans argument : n'importe quel utilisateur connecté. `current_user_id()` donne l'appelant.
- **Mots de passe et codes** : hachés en scrypt (`utils/passwords.py`), jamais en clair, jamais
  dans les logs. 5 échecs en 15 minutes par numéro bloquent la connexion ou l'activation
  (`utils/rate_limit.py`, en mémoire).

### Temps réel

Flask-SocketIO, donc protocole **Socket.IO** : le front utilisera `socket.io-client`, pas un
`WebSocket` natif. Un salon par course (`ride:{id}`). Les services émettent via
`sockets/broadcast.py` **après** la validation de leur transaction.

### Journalisation

Sortie standard, une ligne JSON par événement (`LOG_FORMAT=text` en dev). Une ligne par requête
avec un identifiant renvoyé dans `X-Request-Id`. **Jamais** dans les logs : mot de passe, jeton,
e-mail, téléphone, adresse, position d'un usager (RGPD). On journalise l'identifiant, pas
l'identité. Le détail technique d'une erreur va dans les logs, jamais dans la réponse.

---

## 2. Front-end (`FRONTEND/`)

### Technologies

| Rôle | Bibliothèque |
|---|---|
| Interface | React 19 + TypeScript 6 |
| Build | Vite 8 |
| Navigation | react-router-dom 7 |
| PWA (installable, coquille hors ligne) | vite-plugin-pwa |
| Types de l'API | openapi-typescript (génération) |
| Lint | oxlint |
| Style | CSS maison avec variables, **sans framework** |

À ajouter quand l'étape arrive, pas avant : Leaflet (carte, étape 4), socket.io-client (temps
réel, étape 4). Peu de dépendances : chaque Ko compte sur le réseau guyanais.

### Dossiers

```
FRONTEND/src/
├── main.tsx / App.tsx       Point d'entrée, routeur
├── api/                     Seule couche qui parle au réseau
│   ├── client.ts            Le seul fetch du projet (cookie, délai max, erreurs)
│   └── health.ts            Une fonction par appel, typée depuis types/api.ts
├── types/api.ts             GÉNÉRÉ depuis l'OpenAPI du back, jamais modifié à la main
├── lib/                     Logique pure, sans React (messages d'erreur, calculs, formats)
├── hooks/                   Orchestration d'un écran : appel, chargement, erreur, nouvelle tentative
├── context/                 Providers d'état global (SessionProvider : l'utilisateur connecté)
├── components/
│   ├── ui/                  Éléments réutilisables (RequestState : chargement / erreur / réessayer)
│   └── layout/              Cadre commun (Layout)
├── pages/                   Une page par route : assemble des composants, décide de la navigation
├── routes/AppRoutes.tsx     Déclaration des routes
└── styles/global.css        Variables et styles globaux
```

| Dossier | Contient | Ne contient **jamais** |
|---|---|---|
| `api/` | Fonctions qui appellent l'API | React, état, affichage |
| `types/` | Types générés | Code écrit à la main |
| `lib/` | Fonctions pures | React, appel réseau |
| `hooks/` | Appel + état de chargement + message d'erreur | JSX |
| `components/` | Ce qui s'affiche | Appel réseau direct |
| `pages/` | Assemblage et navigation | Logique métier |

Parallèle avec le back : `pages/`, `components/` ≈ `controllers/` ; `hooks/` ≈ `services/` ;
`api/` ≈ `repository/`.

### Règles

- **Un seul `fetch`**, dans `api/client.ts` (cookies, en-tête CSRF, renouvellement de session).
- **Types générés** : après tout changement d'un DTO, lancer le back puis `npm run api:types`.
  TypeScript signale ensuite tous les écrans cassés.
- **Chaque appel a un état de chargement et un état d'erreur avec « Réessayer »**
  (`RequestState`). Le client abandonne une requête au bout de 15 s.
- **Un composant n'appelle jamais `api/`** : il passe par un hook.
- **Le front ne protège rien** : masquer un écran évite une erreur de manipulation, la vraie
  vérification du rôle est dans le back. `useSession()` donne l'utilisateur connecté ;
  `routes/AccessRoutes.tsx` redirige un visiteur vers `/connexion`.
- **Formulaires** : `components/form/` (`Form`, `TextField`, `PasswordField`, `CheckboxField`) et
  le hook `useSubmit`, qui place les erreurs du back sous chaque champ.
- **Du texte, jamais du HTML** : `dangerouslySetInnerHTML` interdit sur une donnée utilisateur.
- **Public peu à l'aise avec le numérique** : textes courts et simples, gros boutons
  (`--touch-target`), contraste fort, focus visible, animations coupées si
  `prefers-reduced-motion`.
- **Aucune couleur, taille ou marge en dur** : tout passe par les variables de `global.css`, selon
  la [charte graphique](charte-graphique.md).
- Un composant qui dépasse une centaine de lignes a presque toujours deux responsabilités.

---

## 3. Ajouter une fonctionnalité — liste de contrôle

1. Le besoin est-il dans le MVP (`CLAUDE.md`) ? Demande-t-il une table ? → équipe BD d'abord.
2. `dtos/` : modèle d'entrée et de sortie.
3. `repository/` : lectures et écritures.
4. `services/` : règles, droits, transaction unique ; tests pytest.
5. `controllers/` : la route, avec tous ses codes d'erreur dans `@spec.validate`.
6. `sockets/` : l'événement temps réel éventuel, émis par le service.
7. `@require_login(...)` sur la route, et un test qui prouve qu'un rôle non autorisé est refusé.
8. Front : `npm run api:types`, puis `api/` → `hooks/` → `components/` → `pages/` → `routes/`.
9. `pytest`, `npm run lint`, `npm run build` passent.
