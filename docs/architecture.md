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

Versions figées dans `requirements.txt`. Base : MySQL 8.4 en local dans Docker (`compose.yaml`,
`sql/schema-mvp.sql`), pilote PyMySQL. Les tests tournent sur SQLite en mémoire.

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
- **Services externes** (adresses et distance par la route : OpenRouteService, H13) : appelés
  depuis `repository/` aussi, qui reste « la source des données », base ou pas
  (`place_repository.py`). Une panne y lève une exception propre au repository, que le service
  traduit en `503`. Sans `ORS_API_KEY`, données factices et aucun appel à Internet (tests, CI).
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
| 503 | Un service externe dont dépend la route ne répond pas (adresses, distance) |

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

### Ce que chacun voit d'une course

Une course renvoyée par l'API dépend de **qui la demande**. `ride_service.present()` ajoute à
chaque course ce que l'appelant a le droit de savoir de l'autre partie, et rien d'autre :

- `driver` (prénom, véhicule, note moyenne) pour l'usager de la course et le personnel ; son
  téléphone seulement pendant la course (`accepted`, `in_progress`) ;
- `rider` (prénom, téléphone) pour le chauffeur de la course pendant la course, et le personnel ;
  **jamais** sur une offre.

Tout service qui renvoie des courses passe par `present()`. Les champs `rating`, `driver` et
`rider` de `Ride` ne sont jamais écrits par le repository (ce sont des jointures).

### Transitions d'une course

Chaque changement de statut est une écriture conditionnelle sur le statut attendu
(`ride_repository.update_if_status`, contrat 6.2) : de deux actions simultanées (deux chauffeurs
qui acceptent, une annulation et un démarrage), une seule gagne, l'autre reçoit `409`. Refaire
une transition déjà faite par le même acteur renvoie la course, pas une erreur (bouton touché
deux fois en 2G). Règles et délais : `services/ride_rules.py` ; côté chauffeur :
`services/driver_service.py`.

### Temps réel

**Pas encore en place (étape 4)** : aujourd'hui, tout passe par HTTP et les écrans ont un bouton
« Actualiser ». Il restera comme secours quand le temps réel arrivera.

Flask-SocketIO, donc protocole **Socket.IO** : le front utilisera `socket.io-client`, pas un
`WebSocket` natif. Un salon par course (`ride:{id}`). Les services émettent via
`sockets/broadcast.py` **après** la validation de leur transaction. Événements prévus par le
contrat (partie 5) : `ride:updated`, `ride:offer`, `ride:offer-closed`, `driver:location`.

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
│                            (useRequest : le modèle générique d'un chargement, à réutiliser)
├── context/                 Providers d'état global (SessionProvider : l'utilisateur connecté)
├── components/
│   ├── ui/                  Éléments réutilisables (RequestState : chargement / erreur / réessayer)
│   └── layout/              Cadre commun : Layout (en-tête), PageHero (bandeau vert et titre),
│                            PageSheet (feuille blanche du contenu)
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
  (`RequestState`). Le client abandonne une requête au bout de 15 s. Mais l'écran n'attend pas
  le réseau quand il peut faire sans (voir [Réseau faible](#réseau-faible--objectif-regular-2g)).
- **Un composant n'appelle jamais `api/`** : il passe par un hook. Pour charger des données,
  `useRequest` (chargement, erreur, « Réessayer », valeur déjà connue affichée sans appel) plutôt
  qu'un hook écrit à la main ; pour un envoi de formulaire, `useSubmit`.
- **Chaque écran** : `PageHero` (le titre, dans le bandeau vert) puis `PageSheet` (le contenu),
  selon la [charte graphique](charte-graphique.md#5-mise-en-page).
- **Le front ne protège rien** : masquer un écran évite une erreur de manipulation, la vraie
  vérification du rôle est dans le back. `useSession()` donne l'utilisateur connecté ;
  `routes/AccessRoutes.tsx` redirige un visiteur vers `/connexion`.
- **Formulaires** : `components/form/` (`Form`, `TextField`, `PasswordField`, `CheckboxField`) et
  le hook `useSubmit`, qui place les erreurs du back sous chaque champ.
- **Action lourde** (annuler, se désister) : `components/ui/ConfirmButton`, confirmée sur place.
- **Écran d'un objet ouvert depuis une liste** : la liste passe l'objet dans l'état de navigation
  (`state={{ ride }}`), l'écran l'affiche sans appel (`useRide(id, known)`). Après une action,
  l'écran remplace cet état (`navigate(…, { replace: true, state })`) pour que « Retour » ne
  montre pas l'ancien état.
- **Position du chauffeur** : `context/DriverLocationProvider` (monté dans `Layout`) l'envoie en
  fond tant que le chauffeur est disponible ; règles d'envoi dans `lib/locationSharing.ts`. En
  PWA, l'envoi s'arrête quand l'application passe en arrière-plan.
- **Du texte, jamais du HTML** : `dangerouslySetInnerHTML` interdit sur une donnée utilisateur.
- **Public peu à l'aise avec le numérique** : textes courts et simples, gros boutons
  (`--touch-target`), contraste fort, focus visible, animations coupées si
  `prefers-reduced-motion`.
- **Aucune couleur, taille ou marge en dur** : tout passe par les variables de `global.css`, selon
  la [charte graphique](charte-graphique.md).
- Un composant qui dépasse une centaine de lignes a presque toujours deux responsabilités.

### Réseau faible : objectif « Regular 2G »

Le public utilise souvent un téléphone d'entrée de gamme sur un réseau 2G ou 3G faible. Chaque
fonctionnalité est vérifiée sur le profil **« Regular 2G »** des DevTools (250 kbit/s, 300 ms
d'aller-retour) avant sa pull request :

| Moment | Objectif |
|---|---|
| Première visite | Quelque chose d'utile à l'écran en moins de **1 s**, écran utilisable en moins de **5 s** |
| Réouverture (application en cache) | L'écran s'affiche **sans attendre le réseau** |
| Toute action | Une réponse visible tout de suite (bouton désactivé, « Envoi en cours… ») |

Sur ce réseau, **c'est le nombre d'allers-retours qui coûte, plus que le poids** : chacun prend au
moins 300 ms. Mesuré au 20/10/2026 : 90 Ko de JS ≈ 3 s, un aller-retour ≈ 0,35 s.

**Ce qui est en place, et à suivre pour chaque nouvel écran :**

1. **L'écran avant le JavaScript.** `index.html` contient l'écran d'accueil en HTML (copie de
   `Layout.tsx` et `WelcomePage.tsx`, à modifier ensemble), affiché dès l'arrivée du CSS. Un petit
   script y montre « Chargement… » à la place pour une autre page ou un utilisateur déjà connecté.
2. **Chargement optimiste de la session.** Aucun écran n'attend `/auth/me`. `SessionProvider`
   part de l'indice laissé par la dernière session (`lib/sessionHint.ts` : prénom et rôle
   seulement, effacé à la déconnexion) ; l'API confirme ou corrige ensuite. Un écran de
   l'utilisateur connecté s'affiche donc avec `user ?? hint`, et lance ses propres appels sans
   attendre la session.
3. **Allers-retours comptés.** Les cookies CSRF lisibles disent l'état de la session sans appel
   (`storedSession()` dans `api/client.ts`) : aucun appel pour un visiteur, un seul pour un
   utilisateur connecté (`/auth/refresh` renvoie aussi le compte). Côté back, la réponse aux
   requêtes de contrôle CORS (`OPTIONS`, avant chaque écriture) est gardée 2 h par le navigateur
   (`CORS_PREFLIGHT_MAX_AGE_SECONDS`). En production, servir l'API sur la même origine que le
   front les supprimerait toutes.
4. **Dire ce qui se passe.** Après 3 s d'attente, `LoadingMessage` et `Form` disent que le
   réseau est lent et que ça continue (`useSlowNetwork`). Sans réseau, `Layout` affiche un
   bandeau (`useOnline`) et relit la session dès son retour.
5. **Chaque nouvel appel se demande** : peut-il partir en même temps qu'un autre plutôt
   qu'après ? Sa réponse peut-elle être affichée d'avance (dernière valeur connue) ? Faut-il
   l'empêcher de partir deux fois (une réservation qui part deux fois sur un réseau lent) ?
6. **Lourdeurs à venir** : charger Leaflet seulement sur l'écran de la carte (`React.lazy`),
   donner d'abord l'information en texte (« Votre chauffeur arrive dans 4 min »), mettre en cache
   les tuiles déjà vues.

**Tester** (Chrome ou Edge) :

```
cd FRONTEND && npm run build && npm run preview
```

(`preview` écoute sur le port 5173, celui qu'autorise le CORS du back.) **Jamais `npm run dev`
pour cette mesure** : Vite y sert des centaines de modules non regroupés, dont React en version de
développement (plus de 1 Mo) ; en Regular 2G, plus de 20 s. L'écran d'avant le JavaScript doit
quand même y rester lisible : le CSS est lié dans `index.html` (pas importé par `main.tsx`) et
chaque SVG porte une largeur et une hauteur par défaut. Dans les DevTools, onglet **Network**, choisir **Regular 2G**, puis :
- **première visite** : cocher « Disable cache » et vider le service worker (onglet Application →
  Storage → Clear site data) ;
- **réouverture** : décocher « Disable cache », recharger ;
- regarder quand l'écran devient utile (onglet Performance ou captures de Network) et combien
  d'appels à l'API partent, puis refaire le parcours de la fonctionnalité.

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
10. Parcours testé en **« Regular 2G »** : objectifs du tableau
    [ci-dessus](#réseau-faible--objectif-regular-2g) tenus, aucun aller-retour évitable.
