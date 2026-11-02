# Audit de sécurité — 2 novembre 2026

Périmètre : tout le dépôt sur la branche `feature/driver-earnings` (commit `c75e612`), back Flask, front React, SQL, Docker, CI, dépendances. Phase 1, **en lecture seule** : aucun fichier du projet n'a été modifié (hors ce rapport). Les corrections sont venues ensuite, sur la branche `fix/security-audit` : voir la [partie G](#g-corrections). Les preuves ont été faites avec le client de test Flask, sur les données factices en mémoire, sans appel à un service extérieur.

## A. Résumé

**État général : bon socle, quelques trous de conception à fermer avant tout déploiement.** Le contrôle d'accès objet par objet (IDOR/BOLA) est correct sur toutes les routes testées, les jetons sont hors de portée du JavaScript, la protection CSRF fonctionne, les entrées sont validées strictement (champ inconnu → 400, pas d'affectation de masse), aucune injection n'est possible aujourd'hui (pas encore de SQL, appel ORS à URL fixe et paramètres encodés), aucun secret dans l'historique Git, aucune vulnérabilité dans les dépendances livrées au navigateur.

Les faiblesses sont surtout dans la **gestion des sessions et des comptes** (impossible de couper une session, comptes de démo toujours chargés, inscription sans preuve du numéro) et dans **l'absence de limites de débit** hors connexion.

| Sévérité | Nombre |
|---|---|
| Critique | 0 (1 le deviendrait au déploiement : F1) |
| Élevée | 2 |
| Moyenne | 5 |
| Faible | 8 |
| Information | 5 |

**Les plus urgents**
1. **F1** — Les comptes de démonstration, dont un administrateur au mot de passe publié dans le README, sont chargés sans condition par le code **et** par `sql/schema-mvp.sql`. Tout environnement déployé tel quel est administrable par n'importe qui.
2. **F2** — Un administrateur suspendu garde ses droits 15 minutes : il peut **se réactiver lui-même** et créer un autre compte administrateur. Un compte admin compromis ne peut donc pas être neutralisé.
3. **F3** — Une session ouverte dure 30 jours et rien ne la coupe : ni le changement de mot de passe, ni un nouveau code d'activation, ni la déconnexion ailleurs. Grave pour un public qui partage souvent un téléphone.

## B. Tableau de synthèse

| Id | Titre | Sévérité | Confiance | Emplacement | Correction | Statut |
|---|---|---|---|---|---|---|
| F1 | Comptes de démo (dont admin) toujours chargés, mot de passe public | Élevée (Critique si déployé) | Confirmé | `repository/user_repository.py:220-273`, `sql/schema-mvp.sql:332-350`, `README.md:143-159` | Facile | Corrigé |
| F2 | Admin suspendu : se réactive et crée des admins pendant 15 min | Élevée | Confirmé | `utils/access.py:61-80`, `services/admin_service.py:159-162` | Facile | Corrigé |
| F3 | Sessions non révocables (30 jours), survivent au changement de mot de passe | Moyenne | Confirmé | `utils/access.py:38-58`, `services/auth_service.py:134-144`, `services/user_service.py:49` | Moyenne (schéma BD) | Corrigé (colonne demandée à l'équipe BD) |
| F4 | Inscription sans preuve du numéro : préemption et énumération des numéros | Moyenne | Confirmé | `services/auth_service.py:52-53` | Moyenne (SMS) | Corrigé |
| F5 | Déni de service par scrypt (≈110 ms CPU, 32 Mo par appel) sans limite globale | Moyenne | Confirmé (mesuré) | `services/auth_service.py:78-131`, `utils/rate_limit.py` | Moyenne | Corrigé |
| F6 | Aucune limite sur réservations, estimations, recherches (quota ORS) | Moyenne | Confirmé | `controllers/ride_controller.py:29-80`, `controllers/place_controller.py:26` | Moyenne | Corrigé (plafond à confirmer avec la cliente) |
| F7 | Longueur de la clé de signature JWT non imposée | Moyenne (si clé faible) | Confirmé (lecture) | `main.py:46-50`, `config.py:43,67` | Facile | Corrigé |
| F8 | Compte suspendu : 15 min d'accès complet (usager, opérateur) | Faible | Confirmé | `utils/access.py:61-80` | Facile | Corrigé |
| F9 | Adresse et commune non liées aux coordonnées | Faible | Confirmé | `dtos/ride_dto.py:25-39`, `services/place_service.py:37-41` | Moyenne | Corrigé (lieux signés) |
| F10 | Tout chauffeur, même hors ligne, lit les courses en attente (adresses, motif santé) | Faible | Confirmé | `services/ride_service.py:225-228` | Facile | Corrigé |
| F11 | Page Swagger publique, scripts CDN non figés et sans SRI, sur l'origine de l'API | Faible | Confirmé | `utils/security_headers.py:20`, `flask_pydantic_spec/page.py` | Facile | Corrigé |
| F12 | Pas d'en-têtes `Cache-Control: no-store` ni HSTS | Faible | Confirmé | `utils/security_headers.py` | Facile | Corrigé |
| F13 | Déconnexion sans CSRF | Faible | Confirmé | `controllers/auth_controller.py:98-104` | Facile | Corrigé |
| F14 | Mot de passe actuel sans limite d'essais (`PATCH /users/me`) | Faible | Confirmé (lecture) | `services/user_service.py:47` | Facile | Corrigé |
| F15 | Courses de concurrence (limiteur, double acceptation) | Faible | Probable | `utils/rate_limit.py:27-33`, `services/driver_service.py:136-152` | Moyenne | Corrigé en mémoire (verrou SQL à écrire) |
| F16 | Werkzeug 3.1.8 : CVE-2026-102598 | Info | Confirmé, non exploitable ici | `requirements.txt:7` | Facile | Corrigé (3.1.9) |
| F17 | 14 failles npm dans la chaîne de build (dev seulement) | Info | Confirmé | `FRONTEND/package-lock.json` | Facile | Surveillé par la CI |
| F18 | Serveur de développement et mode debug sans garde-fou pour la production | Info | Confirmé (lecture) | `app/__main__.py:10-16`, `BACKEND/.env.example:20` | Facile | Corrigé (refus au démarrage) |
| F19 | Pouvoirs d'administration sans contre-pouvoir | Info | Confirmé (lecture) | `services/admin_service.py:223-233` | Conception | Corrigé (SMS au titulaire) |
| F20 | Points à préparer pour l'étape 4 et la vraie BD | Info | — | `sockets/__init__.py:24`, `repository/user_repository.py:153` | — | CI faite ; Socket.IO, LIKE et CSP du front à prévoir |

## C. Fiches détaillées

### F1 — Comptes de démonstration toujours chargés, admin au mot de passe public

1. **Description.** Huit comptes fictifs (usagers, chauffeur, opérateur, **administrateur**) partagent un mot de passe écrit en clair dans le code et dans le README. Un usager a un code d'activation connu, valable 365 jours.
2. **Emplacement.** `BACKEND/app/repository/user_repository.py:220-259` (comptes), `:273` (`reset()` appelé à l'import du module, sans condition) ; `sql/schema-mvp.sql:332-350` (mêmes comptes et hachages, chargés dans le conteneur) ; `README.md:143-159`.
3. **Cause.** Données de démo et données réelles ne sont pas séparées ; aucun drapeau d'environnement.
4. **Exploitation.** Le jour où l'API tourne quelque part d'accessible (démo client, préproduction, production qui réutilise `schema-mvp.sql`), n'importe qui se connecte en administrateur avec le numéro et le mot de passe du README : liste de tous les comptes (noms, téléphones, e-mails), suspension de chauffeurs, émission de codes d'activation pour prendre n'importe quel compte.
5. **Reproduction (faite).** `POST /auth/login {"phone":"0694000006","password":<mot de passe du README>}` → 200, `role: admin`.
6. **Conséquences.** Prise de contrôle totale ; fuite de données personnelles (RGPD).
7. **Correctif.** Charger les comptes de démo seulement si `LOAD_DEMO_DATA=true` (absent par défaut) ; refuser de démarrer avec ce drapeau si `COOKIE_SECURE=true` ou hors debug. Côté SQL, déplacer les `INSERT` de test dans un `sql/demo-data.sql` séparé que la production ne charge pas (à demander à l'équipe BD). Le premier administrateur réel se crée par une commande d'installation, avec un code d'activation.
8. **Exemple.**
   ```python
   # config.py
   LOAD_DEMO_DATA: bool = _optional("LOAD_DEMO_DATA", "false").lower() == "true"
   # main.py, dans create_app()
   if config.LOAD_DEMO_DATA:
       if config.JWT_COOKIE_SECURE:
           raise MissingConfiguration("LOAD_DEMO_DATA est réservé au développement local.")
       user_repository.load_demo_accounts()
       ride_repository.load_demo_rides()
   ```
9. **Test de régression.**
   ```python
   def test_no_demo_account_without_the_flag(monkeypatch):
       monkeypatch.setattr(Config, "LOAD_DEMO_DATA", False)
       user_repository.reset()
       app = create_app(Config)
       response = app.test_client().post("/auth/login", json={"phone": ADMIN_PHONE, "password": DEV_PASSWORD})
       assert response.status_code == 401
   ```
10. **Références.** CWE-798, CWE-1188 ; OWASP A07:2021 (Identification and Authentication Failures), A05 (Security Misconfiguration).

### F2 — Un administrateur suspendu se réactive lui-même et crée des admins

1. **Description.** `@require_login` ne lit que le jeton d'accès (15 min). Un admin suspendu peut donc continuer à appeler `/admin/*`. `update_account` interdit de **se suspendre** soi-même, mais pas de **se réactiver**.
2. **Emplacement.** `BACKEND/app/utils/access.py:61-80` ; `BACKEND/app/services/admin_service.py:159-162` (`elif changes.status == ACTIVE`).
3. **Cause.** Statut du compte jamais relu sur les routes ; règle « pas sur soi-même » appliquée dans un seul sens.
4. **Exploitation.** Un compte admin est volé (F1, hameçonnage, téléphone perdu). L'autre admin le suspend. Dans les 15 minutes, l'attaquant : `POST /admin/users` (nouvel admin + code d'activation), puis `PATCH /admin/users/<son id> {"status":"active"}`. La suspension est annulée et une porte dérobée durable existe.
5. **Reproduction (faite).** Admin A suspend admin B (200) ; B crée un admin (201) ; B se réactive (200, `status: active`).
6. **Conséquences.** Impossible de contenir la compromission d'un compte admin.
7. **Correctif.** Pour les rôles `admin` et `operator`, relire le compte à chaque requête (une lecture par clé primaire, coût négligeable) et refuser s'il est suspendu. Interdire toute modification de son propre statut.
8. **Exemple.**
   ```python
   # utils/access.py
   def require_login(*roles: str, check_account: bool = False) -> Callable:
       ...
           if check_account or get_jwt().get(_ROLE_CLAIM) in _STAFF_ROLES:
               auth_service.session_user(g.user_id)  # 401 si suspendu ou supprimé
   # services/admin_service.py, update_account
   if changes.status is not _UNCHANGED and user.id == admin_id:
       raise UnprocessableEntity(NOT_YOURSELF)
   ```
   (`utils/` ne doit pas importer un service : passer par une fonction injectée au démarrage, comme `register_jwt_callbacks`.)
9. **Test de régression.**
   ```python
   def test_a_suspended_admin_loses_access_at_once(client, app):
       other = app.test_client(); login(other, OTHER_ADMIN_PHONE)
       login(client, ADMIN_PHONE)
       update(other, ADMIN_ID, status="suspended")
       assert update(client, ADMIN_ID, status="active").status_code == 401
       assert create(client, {...}).status_code == 401
   ```
10. **Références.** CWE-613, CWE-285 ; OWASP API5:2023 (BFLA), A01:2021.

### F3 — Sessions non révocables

1. **Description.** Le jeton de renouvellement vaut 30 jours. `/auth/refresh` vérifie que le compte existe et n'est pas suspendu, mais rien ne relie le jeton au mot de passe courant. Pas de liste de révocation.
2. **Emplacement.** `utils/access.py:38-58` ; `services/auth_service.py:134-144` ; `services/user_service.py:49` (changement de mot de passe) ; `services/auth_service.py:124` (activation après « mot de passe oublié »).
3. **Cause.** Jetons sans état et sans « version de session ».
4. **Exploitation.** Téléphone partagé (association, mission locale), volé ou perdu : la victime change son mot de passe depuis un autre appareil, ou fait émettre un nouveau code par le centre d'appel. La session sur l'ancien téléphone continue 30 jours (réservations au nom de la victime, lecture de ses trajets, de son adresse et de son téléphone).
5. **Reproduction (faite).** Connexion sur A ; connexion sur B, changement de mot de passe, déconnexion ; rejeu du cookie de A sur `/auth/refresh` → 200, puis `/auth/me` → 200.
6. **Conséquences.** Usurpation durable d'un compte ; aucun moyen pour l'admin de couper une session hors suspension.
7. **Correctif.** Ajouter au compte un compteur `session_version` (ou `password_changed_at`), le mettre dans les deux jetons, l'incrémenter au changement de mot de passe, à l'activation et sur action « déconnecter partout » ; `/auth/refresh` refuse si la version diffère. **Changement de schéma : à demander à l'équipe BD**, ne pas l'appliquer ici. En attendant : raccourcir le refresh (7 jours) est un palliatif.
8. **Exemple.**
   ```python
   def start_session(response, user):
       claims = {_ROLE_CLAIM: user.role, "sv": user.session_version}
       set_access_cookies(response, create_access_token(str(user.id), additional_claims=claims))
       set_refresh_cookies(response, create_refresh_token(str(user.id), additional_claims={"sv": user.session_version}))
   # auth_service.session_user(user_id, session_version)
   if user.session_version != session_version:
       raise Unauthorized(SESSION_ENDED)
   ```
9. **Test de régression.** Le scénario du point 5, qui doit finir en 401.
10. **Références.** CWE-613 ; OWASP A07:2021 ; ASVS 3.3.

### F4 — Inscription sans preuve du numéro

1. **Description.** N'importe qui crée un compte usager sur n'importe quel numéro, sans SMS de confirmation. La réponse 409 révèle qu'un numéro a déjà un compte, alors que la connexion prend soin de ne pas le révéler (`verify_or_waste_time`).
2. **Emplacement.** `services/auth_service.py:52-53` ; `controllers/auth_controller.py:30-51`.
3. **Cause.** Le numéro sert d'identifiant sans vérification de possession.
4. **Exploitation.** (a) Énumération : tester des numéros pour savoir qui utilise le service (public fragile, cible d'arnaques). (b) Préemption : enregistrer le numéro d'une personne ; elle ne peut plus s'inscrire et ne sait pas pourquoi ; le centre d'appel non plus.
5. **Reproduction (faite).** `POST /auth/register` avec `0694000001` → 409 ; avec un numéro tiers libre → 201.
6. **Conséquences.** Fuite d'appartenance (RGPD), déni de service ciblé, confusion d'identité pour l'opérateur (étape 6).
7. **Correctif.** Inscription en deux temps : envoi d'un code par SMS (simulé en MVP, comme UC62), compte créé seulement après le code. Réponse identique que le numéro existe ou non (« Nous vous avons envoyé un code »). Avec le centre d'appel, un compte existant se reprend par code d'activation. **Décision produit à valider avec la cliente** (coût des SMS).
8. **Exemple.** `POST /auth/register` → 202 toujours ; `POST /auth/register/confirm {phone, code, ...}` → 201.
9. **Test de régression.** Deux inscriptions, numéro libre et numéro pris : même code HTTP, même corps.
10. **Références.** CWE-204, CWE-287 ; OWASP API2:2023.

### F5 — Déni de service par le hachage scrypt

1. **Description.** Chaque connexion, inscription ou activation fait un scrypt (n=32768, r=8 : **≈112 ms de CPU et 32 Mo de mémoire mesurés**). Le limiteur compte par numéro : des numéros aléatoires ne sont jamais bloqués. Le dictionnaire du limiteur garde une clé par numéro tenté, sans jamais la retirer.
2. **Emplacement.** `services/auth_service.py:78-131` ; `utils/rate_limit.py:43-48` ; `utils/passwords.py:14-33`.
3. **Cause.** Pas de limite globale ni par adresse IP, travail coûteux avant toute limite.
4. **Exploitation.** 50 requêtes simultanées de connexion avec des numéros différents ≈ 1,6 Go de mémoire et tous les cœurs occupés : l'API ne répond plus à personne. Un seul ordinateur suffit.
5. **Reproduction.** Mesure du coût faite ; l'attaque elle-même n'a pas été lancée (destructive).
6. **Conséquences.** Indisponibilité du service, y compris pour les chauffeurs en course.
7. **Correctif.** Ajouter une limite par adresse IP **large** (par exemple 30 échecs par 15 min, pour ne pas bloquer une association derrière une seule IP, ce que le code veut éviter) et une limite globale de hachages simultanés (`threading.BoundedSemaphore`, au-delà : 429). Purger les clés vides du limiteur. En production, Flask-Limiter ou la limite du proxy inverse.
8. **Exemple.**
   ```python
   _HASHING_SLOTS = threading.BoundedSemaphore(MAX_CONCURRENT_HASHES)
   def verify_or_waste_time(secret_hash, secret):
       if not _HASHING_SLOTS.acquire(timeout=HASH_WAIT_SECONDS):
           raise TooManyRequests(TRY_AGAIN_LATER)
       try: ...
       finally: _HASHING_SLOTS.release()
   ```
9. **Test de régression.** Avec un `MAX_CONCURRENT_HASHES` de 1 et un hachage ralenti par monkeypatch, deux connexions parallèles : la seconde reçoit 429.
10. **Références.** CWE-770, CWE-400 ; OWASP API4:2023.

### F6 — Aucune limite sur réservations, estimations et recherches

1. **Description.** Un usager peut créer et « payer » des centaines de courses ; chaque réservation, estimation ou recherche appelle OpenRouteService avec la clé du projet.
2. **Emplacement.** `controllers/ride_controller.py:29-80` ; `controllers/place_controller.py:26-37` ; `repository/place_repository.py:124`.
3. **Cause.** Pas de règle « une course active à la fois » côté usager, pas de quota.
4. **Exploitation.** (a) 200 fausses courses payées (paiement simulé) inondent l'écran des chauffeurs, qui ne trouvent plus les vraies. (b) Une boucle sur `/places` ou `/rides/estimate` épuise le quota ORS : 503 pour tout le monde jusqu'au lendemain.
5. **Reproduction (faite).** 200 réservations + paiements avec un compte → 200 succès. Le quota ORS n'a pas été testé (pas de clé, pas d'appel externe).
6. **Conséquences.** Service inutilisable ; coût si l'abonnement ORS devient payant.
7. **Correctif.** Règle métier : au plus N courses non terminées par usager (par exemple 1 immédiate + 3 programmées, **à valider avec la cliente**), 422 au-delà. Limite par compte sur `/places` et `/rides/estimate`. Cache court des réponses ORS par (texte, commune).
8. **Exemple.**
   ```python
   open_rides = ride_repository.find_upcoming(session, rider_id=rider_id, driver_id=None, statuses=UPCOMING_STATUSES)
   if len(open_rides) >= MAX_OPEN_RIDES_PER_RIDER:
       raise UnprocessableEntity(TOO_MANY_OPEN_RIDES)
   ```
9. **Test de régression.** La (N+1)e réservation renvoie 422 ; un autre usager réserve toujours.
10. **Références.** CWE-770, CWE-799 ; OWASP API4:2023, API6:2023 (Unrestricted Access to Sensitive Business Flows).

### F7 — Clé de signature JWT de longueur non imposée

1. **Description.** Une `FLASK_SECRET_KEY` de moins de 32 caractères ne produit qu'un avertissement. La même clé signe les JWT (HS256) et sert de clé Flask.
2. **Emplacement.** `main.py:46-50` ; `config.py:43,67`.
3. **Cause.** Contrôle non bloquant.
4. **Exploitation.** Avec une clé faible ou laissée à sa valeur d'exemple, un attaquant qui a un seul jeton (le sien, en créant un compte usager) retrouve la clé hors ligne (hashcat mode 16500), puis signe un jeton `role: admin`.
5. **Reproduction.** Lecture du code ; aucune clé réelle n'a été lue.
6. **Conséquences.** Prise de contrôle admin.
7. **Correctif.** Refuser de démarrer si la clé fait moins de 32 caractères ou vaut `replace-with-a-generated-key` ; clé JWT distincte (`JWT_SECRET_KEY`) dans le `.env`.
8. **Exemple.** `if len(config.SECRET_KEY) < SECRET_KEY_MIN_LENGTH: raise MissingConfiguration(...)`
9. **Test.** `create_app` avec une clé courte lève `MissingConfiguration`.
10. **Références.** CWE-326, CWE-1391 ; OWASP A02:2021.

### F8 — Compte suspendu : 15 minutes d'accès complet

Usager ou opérateur suspendu : réservations, annulations (l'opérateur annule **toutes** les courses) restent possibles jusqu'à 15 min (`utils/access.py:61-80`). Prouvé : usager suspendu → `POST /rides` 201. Choix documenté, acceptable pour l'usager ; à fermer pour l'opérateur avec le correctif de F2 (relire le compte pour les rôles du personnel). CWE-613.

### F9 — Adresse et commune non liées aux coordonnées

Le texte de l'adresse et `communeId` viennent du client et ne sont pas comparés aux coordonnées ; la zone n'est vérifiée que par un rayon de 20 km autour de Cayenne, qui déborde des trois communes (`dtos/ride_dto.py:25-39`, `services/place_service.py:37-41`). Prouvé : arrivée « Aéroport Félix Éboué, Matoury » placée à 100 m de la mairie de Cayenne → 8,08 € au lieu d'environ 17 €. Le chauffeur, guidé par les coordonnées, voit un texte trompeur. Correctif : afficher au chauffeur l'adresse **issue d'ORS** pour ces coordonnées (géocodage inverse) ou signer côté serveur les lieux renvoyés par `/places` et n'accepter qu'eux ; contrôler la commune par polygone quand la zone sera fixée. Test : estimation avec une adresse de commune 3 et un point en commune 1 → 422. CWE-20, CWE-345 ; OWASP API6:2023.

### F10 — Tout chauffeur lit les courses en attente, même hors ligne

`_may_see` accepte `role == "driver" and status == PENDING` sans vérifier que le chauffeur est en ligne ni que son véhicule convient (`services/ride_service.py:225-228`). Les identifiants sont séquentiels : un chauffeur peut parcourir `/rides/1..N` et noter adresses exactes, heures et **motif « santé »** de tous les usagers. Prouvé : chauffeur hors ligne → `GET /rides/10` 200, `purpose: health`. Les chauffeurs sont vérifiés en personne, d'où « Faible ». Correctif : appliquer les mêmes règles que `list_offers` (en ligne, véhicule adapté si besoin) et ne pas renvoyer `purpose` sur une offre si la cliente n'en voit pas l'utilité. Test : chauffeur hors ligne → 404. CWE-639 ; OWASP API1:2023, RGPD (minimisation).

### F11 — Documentation publique, scripts CDN non figés

`/apidoc/swagger` et `/apidoc/redoc` sont publics, sans CSP (`utils/security_headers.py:20`), et chargent `swagger-ui-dist@5` et `redoc/latest` depuis des CDN, sans attribut `integrity`. Ces scripts s'exécutent **sur l'origine de l'API** : ils peuvent lire le cookie CSRF et appeler l'API avec la session d'un admin qui ouvre la page. Exploitable seulement si un CDN ou un paquet est compromis. Correctif : désactiver `/apidoc` en production (ne laisser que `openapi.json` si la CI en a besoin, ou le générer hors ligne). CWE-829, CWE-200 ; OWASP A08:2021.

### F12 — En-têtes de cache et HSTS

Aucune réponse ne porte `Cache-Control: no-store`, dont celles qui contiennent un **code d'activation** (`POST /admin/users`, `/activation-code`), le profil (`/auth/me`) ou la liste des comptes. Pas de `Strict-Transport-Security`. Correctif dans `security_headers.py` : `no-store` par défaut sur toute réponse JSON (la photo garde son `Cache-Control` explicite), HSTS quand `COOKIE_SECURE` est vrai. Test : `GET /auth/me` porte `Cache-Control: no-store`. CWE-524, CWE-319.

### F13 — Déconnexion sans CSRF

`POST /auth/logout` ne vérifie aucun jeton (`controllers/auth_controller.py:98-104`). Un site tiers peut déconnecter un utilisateur par un formulaire auto-soumis (navigation de premier niveau : les cookies `Lax` sont renvoyés). Gêne seulement (un chauffeur déconnecté en course). Correctif : exiger l'en-tête CSRF quand un cookie de session est présent. CWE-352.

### F14 — Mot de passe actuel sans limite d'essais

`PATCH /users/me` vérifie le mot de passe actuel sans limiteur (`services/user_service.py:47`) : quelqu'un qui tient un téléphone déverrouillé peut essayer des mots de passe sans fin pour en prendre le contrôle définitif. Correctif : réutiliser `AttemptLimiter` par `user_id`. CWE-307.

### F15 — Conditions de concurrence (probable)

- Limiteur : `is_blocked` puis `record_failure` ne sont pas atomiques ; des connexions parallèles dépassent les 5 essais (gain limité, scrypt est lent).
- Un chauffeur qui accepte deux courses en même temps passe le contrôle d'horaire des deux (`driver_service.py:136-152`) : la vérification lit les courses tenues, l'écriture conditionnelle ne porte que sur la course acceptée.
- Une suspension et une acceptation simultanées laissent un chauffeur suspendu avec une course.
Sans gravité sur les données factices (verrou global) ; à tester sur MySQL : verrou `SELECT … FOR UPDATE` sur la ligne `chauffeur` pendant l'acceptation. CWE-362.

### F16 — Werkzeug 3.1.8 (CVE-2026-102598, GHSA-g6x2-hccm-hh4m)

`safe_join` accepte les noms de périphériques Windows suivis de `:` (`NUL:`), ce qui bloque la lecture d'un fichier servi par `send_from_directory`. La route `/static/<path>` existe, mais le dossier `app/static` est absent : `GET /static/NUL:` répond 404 (testé). **Non exploitable aujourd'hui.** Passer à `Werkzeug==3.1.9`.

### F17 — Dépendances npm de la chaîne de build

`npm audit --omit=dev` : **0 faille** dans ce qui part au navigateur. `npm audit` complet : 14 failles (3 faibles, 11 moyennes) dans `vite-plugin-pwa`/`workbox-build` (`serialize-javascript`, `ejs`, `deepmerge`, `glob`) et `openapi-typescript` (`minimatch`, `fast-uri`). Elles concernent l'outillage local et la CI, pas l'application. Les correctifs proposés par npm sont des retours en arrière de version majeure : attendre les versions corrigées et relancer `npm audit` à chaque montée de version.

### F18 — Serveur de développement et mode debug

`python -m app` lance le serveur Werkzeug avec `allow_unsafe_werkzeug=True` et le debug de `.env` (`.env.example` met `FLASK_DEBUG=true`). Il écoute sur 127.0.0.1 seulement, donc sans risque aujourd'hui. Au déploiement : serveur de production (gunicorn + `simple-websocket` ou eventlet), `FLASK_DEBUG=false`, et refus de démarrer en debug si `COOKIE_SECURE=true`.

### F19 — Pouvoirs d'administration sans contre-pouvoir

Tout admin crée d'autres admins et émet un code d'activation pour **n'importe quel** compte, y compris un autre admin : il peut alors fixer son mot de passe. Le titulaire n'est pas prévenu ; la seule trace est une ligne de log (qui n'est pas conservée par la BD). Choix de conception à discuter : réserver la création d'admins à une commande d'installation, prévenir le titulaire par SMS d'un nouveau code, journal d'audit en base (demande à l'équipe BD).

### F20 — À préparer pour la suite

- **Socket.IO (étape 4)** : `on_connect` accepte toute connexion sans jeton (`sockets/__init__.py:24`). Avant d'émettre `ride:updated` et `driver:location`, vérifier le JWT du cookie à la connexion et n'entrer dans `ride:<id>` qu'après le même contrôle que `get_ride`.
- **Vraie BD** : la recherche de comptes par nom (`user_repository.find_page`) deviendra un `LIKE` : paramètre lié et échappement de `%` et `_`. Garder `pool_pre_ping`, un utilisateur MySQL sans droit DDL pour l'API.
- **Front en production** : définir une CSP (le script en ligne de `index.html` demande un hash), `frame-ancestors 'none'`, HTTPS.
- **CI** : actions GitHub épinglées par tag et non par empreinte ; pas de `pip-audit`, `npm audit --omit=dev` ni recherche de secrets. Les ajouter coûte peu.

## D. Problèmes de fond

1. **Le statut du compte n'est relu qu'au renouvellement.** F2, F3, F8 viennent de là. Une fonction unique « compte encore autorisé ? » appelée par `require_login` pour le personnel, et une version de session dans les jetons, ferment les trois.
2. **Pas de couche de limitation.** Seuls connexion et activation sont limitées, par numéro. F5, F6, F14 demandent un mécanisme commun (par compte, par IP large, global).
3. **Données de démo mêlées au code et au schéma.** F1 ; même logique pour la future bascule vers MySQL.
4. **Le client est cru sur ce qu'il affiche** (F9) : les lieux devraient venir du serveur.

## E. Plan de remédiation

**Immédiat (avant toute démo hébergée)** : F1, F2, F7, F16 (une montée de version).
**Court terme (avant la mise en service de janvier 2027)** : F3 (demande à l'équipe BD), F4 (avec la cliente), F5, F6, F8, F10, F11, F12, F13, F14.
**Moyen terme** : F9 et F19 (avec la cliente), F15 sur la vraie base, F18 et F20 au choix de l'hébergement, outils de sécurité dans la CI.

## F. Bilan de la phase 1

**Vulnérabilités confirmées par une preuve exécutée** : F1, F2, F3, F4, F6, F8, F9, F10, F13 ; coût mesuré pour F5 ; F16 vérifiée non exploitable.
**Confirmées par lecture du code** : F7, F11, F12, F14, F17, F18, F19.
**À vérifier** : F15 (sur MySQL), quota réel d'ORS (F6), comportement des cookies `Lax` selon le domaine retenu au déploiement.

**Contrôles qui tiennent (testés)** : usager B ne lit, ne paie, n'annule pas la course de A (404) ; usager refusé sur `/admin/*` et `/accept` (403) ; chauffeur refusé sur la course d'un autre ; écriture sans en-tête CSRF → 401 ; champ `role` dans `PATCH /users/me` → 400 ; réponses d'erreur sans trace interne ; mêmes réponses à la connexion pour un numéro existant ou non.

**Zones non auditées** : vraie base MySQL et repositories SQL (pas encore écrits) ; Socket.IO métier (étape 4) ; bons solidaires, opérateur, statistiques (pas encore codés) ; hébergement, proxy, TLS (non choisis) ; appel réel à ORS (pas de clé utilisée, aucun appel externe fait).

**Outils exécutés** : `pip-audit` sur `requirements.txt` (1 avis) ; `bandit` sur `BACKEND/app` (3 alertes : `urlopen` à URL fixe, faux positif ; mot de passe de démo, voir F1 ; message d'erreur, faux positif) ; `npm audit` et `npm audit --omit=dev` ; `pytest` (201 tests, tous verts) ; script de preuves sur le client de test Flask ; recherche de secrets dans tout l'historique Git par expressions régulières (rien trouvé). Installés dans un environnement temporaire hors du dépôt.
**Non disponibles** : Semgrep, CodeQL, Gitleaks, TruffleHog, OSV-Scanner (absents du poste, non installés).

**Vérifications manuelles** : lecture complète des contrôleurs, services, DTO, repositories, `utils/`, `config.py`, `main.py`, du client API du front, des routes protégées, de `vite.config.ts`, `index.html`, `compose.yaml`, de la CI, du `.gitignore` et des données de test SQL ; recherche des puits dangereux du front (`innerHTML`, `eval`, redirections, stockage local).

## G. Corrections

Branche `fix/security-audit` (03/11/2026). Chaque correction a ses tests (`BACKEND/tests/test_startup_safety.py`, `test_session_revocation.py`, `test_registration.py`, `test_limits.py`, `test_place_signatures.py`), dont un refus de rôle.

| Id | Correction |
|---|---|
| F1 | Comptes et courses de démo chargés seulement avec `LOAD_DEMO_DATA=true`, refusé avec `COOKIE_SECURE=true`. Données de test SQL déplacées dans `sql/demo-data.sql`, chargé par `compose.yaml` seulement |
| F2, F3, F8 | Compte relu à chaque requête ; `session_version` dans les jetons, augmentée au changement de mot de passe, à l'activation et à la suspension. Personne ne change son propre statut. Colonne demandée à l'équipe BD (README, partie 5) |
| F4 | Inscription en deux étapes avec un code SMS de 6 chiffres (10 min, 5 essais), gardée en mémoire ; même réponse que le numéro ait un compte ou non. Code fixe `123456` avec `LOAD_DEMO_DATA` |
| F5 | Limites par adresse réseau (30 échecs / 15 min, 10 SMS / h), 3 SMS / h par numéro, au plus 4 hachages simultanés, purge du limiteur, `TRUSTED_PROXY_COUNT` |
| F6 | 1 course immédiate et 3 programmées non terminées par usager ; 60 recherches et estimations par compte en 10 min |
| F7, F18 | Démarrage refusé avec une clé faible ou d'exemple, et en debug avec `COOKIE_SECURE=true` |
| F9 | Lieux signés (HMAC) par `GET /places` et dans chaque course ; estimation et réservation refusent un lieu non signé ou modifié |
| F10 | Une offre n'est lisible que par un chauffeur en ligne dont le véhicule convient |
| F11 | `/apidoc` seulement avec `API_DOCS_ENABLED=true` (développement, CI) |
| F12 | `Cache-Control: no-store` par défaut, HSTS en https |
| F13 | Déconnexion : en-tête CSRF exigé quand une session existe |
| F14 | 5 mots de passe actuels faux en 15 min par compte, puis `429` |
| F15 | Limiteur atomique (`try_record`) ; verrou par chauffeur (acceptation, suspension) et par usager (réservation), en mémoire. À remplacer par `SELECT … FOR UPDATE` avec MySQL |
| F16 | Werkzeug 3.1.9 |
| F19 | SMS (simulé) au titulaire d'un compte déjà activé quand un administrateur émet un nouveau code |
| F20 | CI : `pip-audit`, `npm audit --omit=dev`, Gitleaks (`.gitleaks.toml`). Restent : authentification Socket.IO (étape 4), échappement des `LIKE` (repositories SQL), CSP du front (hébergement) |
