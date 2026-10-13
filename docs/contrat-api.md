# Contrat d'API (version 1, proposition)

Ce document s'adresse à **l'équipe base de données**. Il liste ce que l'API devra faire pour le
MVP, et donc **ce qu'elle devra lire et écrire dans la base**. Il sert de point de départ pour
concevoir le schéma.

- **Ce qu'il fixe** : les routes, les données échangées, les règles métier.
- **Ce qu'il ne fixe pas** : vos tables, vos colonnes, vos noms. Les noms ci-dessous
  (`ride`, `voucher`, `priceCents`…) sont ceux de l'API, en anglais et en camelCase. Vous nommez
  et découpez vos tables comme vous voulez : c'est le code de `repository/` qui fait la traduction.
- **Statut** : proposition des développeurs, rien n'est encore codé. Tout est discutable, en
  particulier les [hypothèses](#7-hypothèses-et-questions-ouvertes) de la fin. Une route qui
  n'est pas dans ce document n'aura pas besoin de la base pour le MVP.

## Ce qui change depuis la version 0

La version 0 a été relue : elle laissait des cas sans réponse. La numérotation des parties n'a
pas bougé, les ajouts sont en fin de partie (6.7, 6.8, H11 à H15).

| Sujet | Changement | Effet sur le schéma |
|---|---|---|
| Requête rejouée sur réseau faible | Clé `clientRequestId` sur la réservation ([6.7](#67-rejouer-une-requête-sans-la-doubler)) | Un champ unique sur la course |
| Course sans chauffeur | Nouveau statut `expired`, champs `expiresAt` et `expiredAt` ([6.8](#68-expiration-des-courses-sans-chauffeur)) | Une valeur de statut, deux champs, un index |
| Chauffeur qui se désiste | La course revient en `pending` (`POST /rides/{id}/release`) au lieu d'être annulée | Aucun |
| Courses programmées | La règle « une course à la fois » ne porte plus que sur les courses **actives** ([3.3](#33-course-ride)) | La contrainte en base suggérée en 6.5 n'est plus possible telle quelle |
| Comptes sans mot de passe | Code d'activation à usage unique ([3.1](#31-compte-utilisateur-user)) | Deux champs sur le compte |
| Paiement | Statut `refunded`, champ `paidAt`, règles sur le moment du paiement | Une valeur de statut, un champ |
| Bons | Dates en heure de Guyane, validité jugée au jour du trajet, règle d'arrondi, code plus long | Longueur du code |
| Position du chauffeur | Effacée quand il passe hors ligne | Aucun (colonnes déjà facultatives) |
| Référent partenaire | Ne voit plus l'identité, les adresses ni le motif des courses financées | Aucun |
| Opérateur | `POST /vouchers/check` et `/rides/estimate` acceptent un `riderId` | Aucun |
| Adresses et distances | Nouvelle route `GET /places`, service externe (H13) | Aucun |
| Temps réel | Salon par chauffeur, événement `ride:updated` | Aucun |

## Sommaire

1. [Conventions](#1-conventions)
2. [Rôles](#2-rôles)
3. [Les données dont l'API a besoin](#3-les-données-dont-lapi-a-besoin)
4. [Les routes](#4-les-routes)
5. [Temps réel](#5-temps-réel)
6. [Les requêtes qui demandent de l'attention](#6-les-requêtes-qui-demandent-de-lattention)
7. [Hypothèses et questions ouvertes](#7-hypothèses-et-questions-ouvertes)

---

## 1. Conventions

| Sujet | Convention de l'API | Ce que ça implique pour la base |
|---|---|---|
| Identifiants | Un `id` par objet | Entier auto-incrémenté ou UUID : **à vous de choisir, et de nous le dire** (les exemples utilisent des entiers) |
| Dates-heures | ISO 8601 en UTC (`2026-10-13T14:30:00Z`) | Stocker en UTC, avec un type date-heure. La Guyane est en UTC−3 : la conversion est faite à l'affichage |
| Dates sans heure | `2026-12-31`, **en heure de Guyane** (`America/Cayenne`, UTC−3, pas d'heure d'été) | Un type date. Ne concerne que la validité des bons : c'est l'API qui calcule « aujourd'hui en Guyane » avant de comparer |
| Montants | Entiers, en **centimes d'euro** (`1250` = 12,50 €) | Un type entier, jamais de flottant |
| Positions | `lat` / `lng` en degrés décimaux (WGS 84) | Deux décimaux, ou un type spatial (PostGIS, etc.) |
| Champ vide | Envoyé à `null`, jamais omis | Les colonnes facultatives sont `NULL`, pas de chaîne vide |
| Listes | Paginées : `?page=1&pageSize=20`, réponse `{ items, page, pageSize, total }` | Chaque liste a besoin d'un tri stable et d'un `COUNT` |
| Suppression | Aucune suppression physique dans le MVP : on change un statut | Pas de `DELETE` côté API |
| Erreurs | `{ "error": "...", "detail": ... }` | Rien |

Codes d'erreur communs à toutes les routes : `400` charge invalide, `401` non connecté, `403` rôle
insuffisant, `404` introuvable ou invisible pour l'appelant, `409` conflit d'état, `422` règle
métier violée. Le détail est dans [architecture.md](architecture.md#contrat-dapi).

---

## 2. Rôles

Chaque compte a **un** rôle.

| Rôle (valeur dans l'API) | Profil | Créé par |
|---|---|---|
| `rider` | Usager, prioritaire ou non (attribut `isPriority`) | Lui-même, ou un opérateur par téléphone |
| `driver` | Chauffeur | Lui-même, puis validé par un administrateur |
| `partner` | Référent d'une structure partenaire | Un administrateur |
| `admin` | Administrateur (tient aussi l'écran opérateur dans le MVP) | Un administrateur |

Le tout premier administrateur ne peut être créé par personne : il doit figurer dans vos données
de départ, sans mot de passe, et s'activer comme les autres comptes créés par un tiers
(voir [3.1](#31-compte-utilisateur-user)).

---

## 3. Les données dont l'API a besoin

Pour chaque objet : les informations que l'API doit pouvoir enregistrer et relire. « Obligatoire »
veut dire que l'API en fournira toujours une valeur.

### 3.1 Compte utilisateur (`User`)

| Champ | Type | Obligatoire | Remarques |
|---|---|---|---|
| `id` | identifiant | oui | |
| `role` | `rider` \| `driver` \| `partner` \| `admin` | oui | |
| `status` | `active` \| `pending` \| `suspended` | oui | `pending` : chauffeur en attente de validation |
| `firstName`, `lastName` | texte | oui | |
| `phone` | texte | oui | **Unique.** Sert d'identifiant de connexion. Format international (`+594…`) |
| `email` | texte | non | Unique s'il est renseigné |
| mot de passe haché | texte (prévoir 255) | non | Jamais en clair. Vide tant que le compte n'est pas activé |
| code d'activation haché | texte (prévoir 255) | non | Jamais en clair. Vide hors période d'activation |
| `activationCodeExpiresAt` | date-heure | non | Fin de validité du code (48 h après sa création) |
| `createdAt` | date-heure | oui | |

**Activation.** Un compte créé par quelqu'un d'autre (usager créé par l'opérateur, référent,
administrateur) n'a pas de mot de passe. Un administrateur génère un code à usage unique, le
transmet à la personne (par téléphone ou en main propre), et celle-ci choisit son mot de passe
avec `POST /auth/activate`. Le même mécanisme sert au mot de passe oublié : pas de
réinitialisation en libre-service tant que les SMS sont simulés (H12). Un usager créé par
téléphone qui n'utilise jamais l'application n'est jamais activé, et c'est normal.

Selon le rôle, des informations en plus :

| Rôle | Champ | Type | Obligatoire | Remarques |
|---|---|---|---|---|
| `rider` | `isPriority` | booléen | oui | Usager prioritaire. Aucun effet automatique dans le MVP (H15) : sert de filtre à l'opérateur et aux statistiques |
| `rider` | `needsAccessibleVehicle` | booléen | oui | Personne à mobilité réduite |
| `driver` | `isAvailable` | booléen | oui | En ligne / hors ligne |
| `driver` | `lastLat`, `lastLng`, `lastLocationAt` | position + date-heure | non | **Dernière position connue seulement**, pas d'historique. Remise à vide quand le chauffeur passe hors ligne (RGPD) |
| `driver` | véhicule : `plate`, `model`, `seats`, `isAccessible` | texte, texte, entier, booléen | oui | Un seul véhicule par chauffeur dans le MVP |
| `partner` | `partnerId` | référence | oui | La structure à laquelle le référent appartient |

### 3.2 Structure partenaire (`Partner`)

| Champ | Type | Obligatoire | Remarques |
|---|---|---|---|
| `id` | identifiant | oui | |
| `name` | texte | oui | |
| `type` | `association` \| `collectivity` \| `company` | oui | |
| `status` | `active` \| `suspended` | oui | Les bons d'une structure suspendue ne sont plus utilisables pour de nouvelles réservations |

Une structure a un ou plusieurs référents.

### 3.3 Course (`Ride`)

| Champ | Type | Obligatoire | Remarques |
|---|---|---|---|
| `id` | identifiant | oui | |
| `clientRequestId` | texte (36) | oui | **Unique.** UUID généré par l'appareil qui réserve, voir [6.7](#67-rejouer-une-requête-sans-la-doubler) |
| `riderId` | référence compte | oui | Le passager |
| `driverId` | référence compte | non | Vide tant qu'aucun chauffeur n'a accepté, et de nouveau vide si le chauffeur se désiste |
| `bookedById` | référence compte | oui | Qui a saisi la réservation : l'usager lui-même, ou l'opérateur |
| `channel` | `app` \| `phone` | oui | Réservation par l'application ou par téléphone |
| `status` | voir ci-dessous | oui | |
| `purpose` | `employment` \| `training` \| `health` \| `administrative` \| `other` | oui | Motif du trajet, sert aux statistiques |
| `pickupAddress`, `pickupLat`, `pickupLng` | texte + position | oui | Départ |
| `dropoffAddress`, `dropoffLat`, `dropoffLng` | texte + position | oui | Arrivée |
| `pickupCommuneId`, `dropoffCommuneId` | référence commune | oui | Choisies par l'usager dans la liste des communes. Pour les statistiques par commune |
| `scheduledAt` | date-heure | non | Vide = course immédiate. Sinon au moins 30 minutes après la réservation |
| `needsAccessibleVehicle` | booléen | oui | Copié du profil de l'usager à la réservation |
| `distanceKm` | décimal | oui | Distance par la route, calculée par l'API à la réservation (H13) |
| `priceCents` | entier | oui | Prix total, **calculé par l'API** et figé à la réservation |
| `voucherId` | référence bon | non | Le bon utilisé, s'il y en a un |
| `voucherAmountCents` | entier | oui | Part payée par le partenaire (0 sans bon) |
| `riderAmountCents` | entier | oui | Part payée par l'usager. `priceCents = voucherAmountCents + riderAmountCents` |
| `paymentStatus` | `not_required` \| `pending` \| `paid` \| `refunded` | oui | Voir « Paiement » ci-dessous |
| `expiresAt` | date-heure | oui | Échéance au-delà de laquelle une course encore `pending` expire, voir [6.8](#68-expiration-des-courses-sans-chauffeur) |
| `createdAt`, `acceptedAt`, `startedAt`, `completedAt`, `cancelledAt`, `expiredAt`, `paidAt` | date-heure | `createdAt` seulement | Une date par changement d'état. `acceptedAt` est remise à vide si le chauffeur se désiste |
| `cancelledById` | référence compte | non | |

Cycle de vie de `status` :

```
            ┌──── désistement ────┐
            ▼                     │
        pending ──────────▶ accepted ──▶ in_progress ──▶ completed
         │    │                 │
         │    └────────┬────────┘
         ▼             ▼
      expired      cancelled
```

| Statut | Signification | Qui déclenche |
|---|---|---|
| `pending` | Réservée, en attente d'un chauffeur | L'usager ou l'opérateur (réservation), le chauffeur (désistement) |
| `accepted` | Un chauffeur l'a prise | Un chauffeur |
| `in_progress` | Le passager est à bord | Le chauffeur de la course |
| `completed` | Terminée | Le chauffeur de la course |
| `cancelled` | Annulée par l'usager ou un administrateur, avant `in_progress` | L'usager de la course, un administrateur |
| `expired` | Aucun chauffeur ne l'a prise à temps | L'API, automatiquement |

**Course active d'un chauffeur.** Une course `in_progress`, ou une course `accepted` qui est
immédiate ou dont `scheduledAt` tombe dans les 60 prochaines minutes. Un chauffeur n'a qu'**une**
course active à la fois, mais il peut avoir accepté plusieurs courses programmées à l'avance, à
condition qu'elles soient espacées d'au moins 60 minutes. Les durées de ce document (60 minutes,
30 minutes, 15 minutes, 48 heures) sont des réglages de l'API, pas des données : rien à stocker.

**Paiement** (simulé dans le MVP, H10 et H14).

- `not_required` : le bon couvre tout (`riderAmountCents = 0`).
- `pending` → `paid` : l'usager paie sa part, à partir de `accepted` et au plus tard après la fin
  de la course. Une course `completed` restée `pending` est un impayé, visible de
  l'administrateur.
- `paid` → `refunded` : la course est annulée après le paiement.
- Pour une réservation par téléphone, c'est l'opérateur qui enregistre le paiement.

### 3.4 Évaluation (`Rating`)

| Champ | Type | Obligatoire | Remarques |
|---|---|---|---|
| `rideId` | référence course | oui | **Une seule évaluation par course** |
| `score` | entier de 1 à 5 | oui | |
| `comment` | texte (500 max) | non | |
| `createdAt` | date-heure | oui | |

L'usager évalue le chauffeur. Pas d'évaluation dans l'autre sens dans le MVP.

### 3.5 Bon solidaire (`Voucher`)

| Champ | Type | Obligatoire | Remarques |
|---|---|---|---|
| `id` | identifiant | oui | |
| `code` | texte (12) | oui | **Unique.** Généré par l'API (`SOL-` + 8 caractères sans lettres ambiguës), saisi par l'usager à la réservation |
| `partnerId` | référence structure | oui | Qui finance |
| `issuedById` | référence compte | oui | Le référent qui l'a émis |
| `beneficiaryId` | référence compte | non | Si renseigné, seul cet usager peut l'utiliser |
| `coveragePercent` | entier de 1 à 100 | oui | 100 = prise en charge totale |
| `maxRides` | entier ≥ 1 | oui | Nombre de courses financées |
| `usedRides` | entier ≥ 0 | oui | `usedRides ≤ maxRides` |
| `validFrom`, `validUntil` | date (heure de Guyane) | oui | Bornes incluses : valable du `validFrom` à 0 h au `validUntil` à minuit, heure de Guyane |
| `status` | `active` \| `revoked` | oui | « Expiré » et « épuisé » se déduisent des dates et du compteur |
| `createdAt` | date-heure | oui | |

Règles :

- **Jour de validité** : le bon doit être valable **le jour du trajet** (le jour de `scheduledAt`
  pour une course programmée, aujourd'hui pour une course immédiate), pas seulement le jour de la
  réservation.
- **Arrondi** : `voucherAmountCents` = `priceCents × coveragePercent / 100`, arrondi au centime
  **supérieur**. L'usager paie le reste : le centime d'arrondi n'est jamais à sa charge.
- **Compteur** : `usedRides` augmente à la réservation, et diminue si la course est annulée ou
  expire. Un désistement du chauffeur ne le touche pas : la course reste réservée.
- **Révocation** : les courses déjà réservées restent financées.

**Traçabilité** (exigée par le cahier des charges) : pour chaque course financée, on doit
retrouver le bon, la structure, le montant pris en charge et la date. C'est le rôle de
`voucherId` et `voucherAmountCents` sur la course : ils ne doivent jamais être effacés, même si
le bon est révoqué ensuite, ni si la course est annulée.

### 3.6 Données de référence

Fournies par vous, lues par l'API, jamais modifiées par elle dans le MVP.

| Donnée | Contenu | Remarques |
|---|---|---|
| Communes | `id`, `name` | Au minimum les trois communes pilotes : Cayenne, Matoury, Kourou |
| Tarif | `baseFareCents` (prise en charge), `perKmCents` (prix au kilomètre) | Un seul tarif dans le MVP. Prévoir qu'il puisse y en avoir plusieurs plus tard (par profil, par type de financement) |
| Premier administrateur | Un compte `admin`, sans mot de passe | Données fictives, voir [2](#2-rôles) |

---

## 4. Les routes

La colonne « En base » résume ce que la route lit (**L**) et écrit (**E**).

### 4.1 Compte et connexion

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `POST /auth/register` | public | Crée un compte `rider` (actif) ou `driver` (en attente, avec son véhicule). `409` si le téléphone existe déjà, y compris pour un compte créé par l'opérateur : il faut alors l'activer | L : téléphone ou e-mail déjà pris ? E : un compte |
| `POST /auth/activate` | public | Téléphone + code d'activation + nouveau mot de passe. Efface le code | L : compte par téléphone. E : mot de passe, code remis à vide |
| `POST /auth/login` | public | Connexion par téléphone + mot de passe | L : compte par téléphone |
| `POST /auth/logout` | connecté | Déconnexion | Rien |
| `GET /auth/me` | connecté | Renvoie le compte connecté et son profil | L : compte par id |
| `PATCH /users/me` | connecté | Modifie son nom, son e-mail, son mot de passe, ses besoins d'accessibilité | E : le compte |

### 4.2 Réservation (usager)

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `GET /communes` | connecté | Liste des communes desservies | L : communes |
| `GET /places` | connecté | Cherche une adresse dans une commune (`?search=&communeId=`) et renvoie des propositions avec leur position | Rien (service externe, H13) |
| `POST /vouchers/check` | `rider`, `admin` | Vérifie un code de bon et renvoie sa prise en charge. L'administrateur précise le `riderId` | L : bon par code, structure |
| `POST /rides/estimate` | `rider`, `admin` | Calcule distance et prix, avec ou sans bon. N'enregistre rien. L'administrateur précise le `riderId` | L : tarif, bon par code |
| `POST /rides` | `rider` | Réserve une course immédiate ou programmée, avec ou sans bon. Recalcule le prix : celui de l'estimation n'est jamais repris tel quel | L : tarif, bon, course par `clientRequestId`. E : une course, **et** `usedRides + 1` sur le bon, dans la même transaction |
| `GET /rides` | `rider`, `driver` | Ses propres courses, filtrables par `status`, les plus récentes d'abord | L : courses par usager ou par chauffeur |
| `GET /rides/{id}` | participant, `admin` | Détail d'une course, avec le prénom du chauffeur, son véhicule et sa note moyenne. La position du chauffeur n'est renvoyée que si la course est active | L : course + chauffeur + véhicule + moyenne des évaluations |
| `POST /rides/{id}/cancel` | `rider` de la course, `admin` | Annule une course `pending` ou `accepted` | E : statut, `usedRides − 1` sur le bon s'il y en avait un, `paymentStatus = refunded` si elle était payée |
| `POST /rides/{id}/payment` | `rider` de la course, `admin` | Paiement simulé de la part de l'usager | E : `paymentStatus`, `paidAt` |
| `POST /rides/{id}/rating` | `rider` de la course | Évalue une course terminée | E : une évaluation (409 s'il y en a déjà une) |

« Participant » : l'usager ou le chauffeur de la course. Quelqu'un d'autre reçoit `404`.

### 4.3 Chauffeur

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `PUT /drivers/me/availability` | `driver` | Se met en ligne ou hors ligne | E : `isAvailable`, et position remise à vide s'il passe hors ligne |
| `PUT /drivers/me/location` | `driver` | Envoie sa position (toutes les quelques secondes quand il est en ligne) | E : dernière position. **Écriture très fréquente** |
| `GET /drivers/me/ride-offers` | `driver` | `?type=immediate` : courses immédiates en attente proches de lui. `?type=scheduled` : toutes les courses programmées en attente, par date. Dans les deux cas, compatibles avec son véhicule | L : voir [6.1](#61-trouver-les-chauffeurs-et-les-courses-proches) |
| `POST /rides/{id}/accept` | `driver` | Prend une course en attente. `409` si elle est déjà prise, ou s'il a déjà une course active ou trop proche | E : voir [6.2](#62-deux-chauffeurs-acceptent-la-même-course) |
| `POST /rides/{id}/release` | `driver` de la course | Se désiste d'une course `accepted` : elle revient en `pending` et est reproposée | E : statut, `driverId` et `acceptedAt` remis à vide, nouvelle `expiresAt` |
| `POST /rides/{id}/start` | `driver` de la course | Passager à bord | E : statut, `startedAt` |
| `POST /rides/{id}/complete` | `driver` de la course | Clôture la course | E : statut, `completedAt` |
| `GET /drivers/me/earnings` | `driver` | Ses revenus sur une période (`?from=&to=`) : total et nombre de courses, par jour | L : somme des `priceCents` de ses courses terminées, groupées par jour (heure de Guyane) |

### 4.4 Bons solidaires (référent partenaire)

Un référent ne voit que les bons de **sa** structure, et jamais le détail des trajets : ni
l'identité du passager, ni les adresses, ni le motif. Le motif n'apparaît que dans les totaux de
la structure. Raison : un motif `health` rattaché à une personne est une donnée sensible (RGPD).

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `POST /vouchers` | `partner` | Émet un bon | E : un bon |
| `GET /vouchers` | `partner` | Liste les bons de sa structure, filtrables par état | L : bons par structure |
| `GET /vouchers/{id}` | `partner` | Détail d'un bon et courses qu'il a financées : date, communes de départ et d'arrivée, statut, montant pris en charge | L : bon + ses courses |
| `POST /vouchers/{id}/revoke` | `partner` | Révoque un bon (les courses déjà réservées restent financées) | E : statut |
| `GET /partners/me/consumption` | `partner` | Suivi sur une période : bons émis, courses financées, montant pris en charge, par mois et par motif | L : agrégats, voir [6.4](#64-statistiques-et-suivi-de-consommation) |

### 4.5 Écran opérateur (réservation par téléphone)

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `GET /operator/riders` | `admin` | Recherche un usager par téléphone ou par nom (`?search=`) | L : recherche sur le téléphone (début) et le nom (contient) |
| `POST /operator/riders` | `admin` | Crée un usager sans mot de passe | E : un compte |
| `POST /operator/rides` | `admin` | Réserve au nom d'un usager | Comme `POST /rides`, avec `channel = phone` et `bookedById` = l'opérateur |

L'opérateur vérifie un bon, estime un prix, annule et enregistre un paiement avec les routes de
la partie 4.2, qui acceptent le rôle `admin`.

### 4.6 Administration

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `GET /admin/users` | `admin` | Liste les comptes, filtrables par rôle et statut, recherche par nom ou téléphone | L : comptes |
| `POST /admin/users` | `admin` | Crée un référent partenaire ou un administrateur, sans mot de passe | E : un compte |
| `PATCH /admin/users/{id}` | `admin` | Valide un chauffeur, suspend ou réactive un compte, marque un usager prioritaire | E : le compte |
| `POST /admin/users/{id}/activation-code` | `admin` | Génère un code d'activation (premier accès ou mot de passe oublié). Le code est affiché une seule fois, remplace le précédent | E : code haché, échéance |
| `GET /admin/partners` | `admin` | Liste les structures | L : structures |
| `POST /admin/partners` | `admin` | Crée une structure | E : une structure |
| `PATCH /admin/partners/{id}` | `admin` | Renomme, suspend ou réactive une structure | E : la structure |
| `GET /admin/rides` | `admin` | Toutes les courses, filtrables par statut, date, commune, état du paiement | L : courses |
| `GET /admin/stats` | `admin` | Statistiques sur une période | L : agrégats, voir [6.4](#64-statistiques-et-suivi-de-consommation) |

### 4.7 Exemples

Une réservation (`POST /rides`). Le prix n'est pas envoyé : l'API le calcule.

```json
{
  "clientRequestId": "0b9c2f4e-6a1d-4c3b-9e7f-2d5a8c1b4e60",
  "purpose": "health",
  "pickup": { "address": "12 rue des Exemples, Cayenne", "lat": 4.9372, "lng": -52.3260, "communeId": 1 },
  "dropoff": { "address": "Centre de santé fictif, Matoury", "lat": 4.8470, "lng": -52.3310, "communeId": 2 },
  "scheduledAt": null,
  "voucherCode": "SOL-4F7K2Q9M"
}
```

Une course (`GET /rides/42`) :

```json
{
  "id": 42,
  "status": "accepted",
  "channel": "app",
  "purpose": "health",
  "pickup": { "address": "12 rue des Exemples, Cayenne", "lat": 4.9372, "lng": -52.3260, "communeId": 1 },
  "dropoff": { "address": "Centre de santé fictif, Matoury", "lat": 4.8470, "lng": -52.3310, "communeId": 2 },
  "scheduledAt": null,
  "needsAccessibleVehicle": false,
  "distanceKm": 11.4,
  "priceCents": 1640,
  "voucherAmountCents": 820,
  "riderAmountCents": 820,
  "paymentStatus": "pending",
  "voucher": { "id": 7, "code": "SOL-4F7K2Q9M", "coveragePercent": 50 },
  "driver": {
    "id": 15,
    "firstName": "Prénom",
    "averageScore": 4.7,
    "vehicle": { "plate": "AA-000-AA", "model": "Modèle fictif", "isAccessible": false },
    "location": { "lat": 4.9301, "lng": -52.3255, "updatedAt": "2026-10-13T14:31:10Z" }
  },
  "rating": null,
  "createdAt": "2026-10-13T14:30:00Z",
  "expiresAt": "2026-10-13T14:45:00Z",
  "acceptedAt": "2026-10-13T14:30:45Z",
  "startedAt": null,
  "completedAt": null,
  "cancelledAt": null,
  "expiredAt": null,
  "paidAt": null
}
```

Un bon (`GET /vouchers/7`), vu par le référent :

```json
{
  "id": 7,
  "code": "SOL-4F7K2Q9M",
  "partnerId": 3,
  "beneficiaryId": null,
  "coveragePercent": 50,
  "maxRides": 10,
  "usedRides": 4,
  "validFrom": "2026-10-01",
  "validUntil": "2026-12-31",
  "status": "active",
  "createdAt": "2026-10-01T09:00:00Z",
  "rides": [
    { "date": "2026-10-13", "pickupCommuneId": 1, "dropoffCommuneId": 2, "status": "accepted", "voucherAmountCents": 820 }
  ]
}
```

---

## 5. Temps réel

Par Socket.IO. **Rien de plus à stocker** : ces événements rediffusent des données déjà
enregistrées par les routes ci-dessus.

Deux sortes de salons : un par course (`ride:{id}`, suivi par l'usager et le chauffeur de la
course) et un par chauffeur (`driver:{id}`, pour lui proposer des courses).

| Événement | Salon | Contenu |
|---|---|---|
| `ride:offer` | `driver:{id}` de chaque chauffeur en ligne proche | Une nouvelle course immédiate en attente (à la réservation, ou après un désistement) |
| `ride:offer-closed` | Les mêmes | La course n'est plus à prendre (acceptée, annulée ou expirée) |
| `ride:updated` | `ride:{id}` | La course complète, après chaque changement d'état |
| `driver:location` | `ride:{id}`, tant que la course est active | La position du chauffeur |

Un événement perdu n'est pas renvoyé. À chaque reconnexion, le front relit l'état par les routes
HTTP (`GET /rides/{id}`, `GET /drivers/me/ride-offers`) : le temps réel accélère l'affichage, il
n'est jamais la seule source.

Les SMS du mode dégradé sont simulés (écrits dans les logs) : pas de table pour le MVP.

---

## 6. Les requêtes qui demandent de l'attention

Les points où le schéma (types, index, contraintes) change vraiment la difficulté du code.

### 6.1 Trouver les chauffeurs et les courses proches

- À la réservation d'une course immédiate : les chauffeurs `active`, `isAvailable`, avec une
  position récente (moins de quelques minutes), sans course active
  ([définition](#33-course-ride)), avec un véhicule accessible si la course le demande,
  **triés par distance** au point de départ.
- Pour `GET /drivers/me/ride-offers?type=immediate` : l'inverse, les courses `pending` sans
  `scheduledAt` dont le départ est dans un rayon donné autour du chauffeur.
- Pour `?type=scheduled` : les courses `pending` avec `scheduledAt`, triées par date, sans filtre
  de distance (la position actuelle du chauffeur ne dit rien de la semaine prochaine).

Avec un type spatial et son index (PostGIS par exemple), c'est une requête simple. Sans, on
filtrera sur un rectangle `lat`/`lng` puis on calculera la distance en Python : faisable à
l'échelle du MVP (15 à 20 chauffeurs), mais il faut alors un index sur les colonnes de position.

### 6.2 Deux chauffeurs acceptent la même course

Un seul doit gagner, l'autre reçoit `409`. L'API fera une mise à jour conditionnelle :

```sql
UPDATE course SET statut = 'accepted', chauffeur_id = :id, accepte_le = :maintenant
WHERE id = :course AND statut = 'pending';
```

et regardera si une ligne a été modifiée. Besoin : un moteur transactionnel (pas de MyISAM).

Toutes les transitions suivent ce modèle (`WHERE statut = <état attendu>`), y compris le
désistement, l'annulation et l'expiration : c'est ce qui départage une annulation et une
acceptation qui arrivent en même temps.

### 6.3 Consommer un bon

Réserver une course avec un bon fait deux écritures dans **une** transaction : créer la course et
incrémenter `usedRides`. Même principe que ci-dessus pour ne jamais dépasser le plafond :

```sql
UPDATE bon SET courses_utilisees = courses_utilisees + 1
WHERE id = :bon AND statut = 'active' AND courses_utilisees < courses_max
  AND :jour_du_trajet BETWEEN valide_du AND valide_au;
```

`:jour_du_trajet` est une date en heure de Guyane, calculée par l'API. La structure doit aussi
être `active`, et le bénéficiaire correspondre s'il est renseigné : vérifié dans la même
transaction.

Libérer un bon (annulation, expiration) est l'opération inverse, sans condition de date ni de
statut :

```sql
UPDATE bon SET courses_utilisees = courses_utilisees - 1
WHERE id = :bon AND courses_utilisees > 0;
```

Une contrainte `CHECK (courses_utilisees BETWEEN 0 AND courses_max)` en base serait une sécurité
bienvenue.

### 6.4 Statistiques et suivi de consommation

Toutes sur une période (`from`, `to`), calculées à la demande (pas de table d'agrégats pour le
volume du MVP, quelques dizaines de courses par jour) :

- nombre de courses par statut, par jour, par commune de départ, par motif, par canal ;
- nombre de courses `expired` : c'est la demande que le service n'a pas su servir ;
- nombre d'usagers et de chauffeurs actifs, part des usagers prioritaires ;
- nombre de courses financées et montant pris en charge, au total et par structure ;
- nombre et montant des impayés (`completed` et `paymentStatus = pending`) ;
- note moyenne, et **part des évaluations à 4 ou 5** (l'objectif du client est « plus de 90 % de
  satisfaction » : c'est une proportion, pas une moyenne) ;
- pour un référent : les mêmes chiffres, limités à sa structure et sans donnée individuelle.

Les regroupements par jour et par mois se font en heure de Guyane.

Besoin : des index sur les dates et les statuts des courses, et des valeurs de statut, de motif
et de commune **contraintes** (clé étrangère ou `CHECK`), sinon les regroupements seront faux.

### 6.5 Unicité et intégrité

| Règle | Où |
|---|---|
| Téléphone unique ; e-mail unique s'il est renseigné | Compte |
| Code unique | Bon |
| `clientRequestId` unique | Course |
| Une évaluation au plus par course | Évaluation |
| `priceCents = voucherAmountCents + riderAmountCents`, montants ≥ 0 | Course |
| `score` entre 1 et 5, `coveragePercent` entre 1 et 100 | Évaluation, bon |
| `driverId` renseigné si et seulement si le statut est `accepted`, `in_progress` ou `completed` (il peut l'être aussi sur une course `cancelled`) | Course |
| Un chauffeur n'a qu'une course active à la fois, et ses courses programmées sont espacées d'au moins 60 minutes | Course. **Vérifié par l'API seulement** : la règle dépend de l'heure, une contrainte en base ne peut pas l'exprimer |

### 6.6 Accès les plus fréquents (pour vos index)

| Accès | Fréquence |
|---|---|
| Compte par id (à chaque requête authentifiée) | Très élevée |
| Mise à jour de la position d'un chauffeur | Très élevée |
| Course par id | Élevée |
| Courses d'un usager / d'un chauffeur, triées par date | Élevée |
| Courses par statut (`pending` surtout) | Élevée |
| Courses `pending` dont `expiresAt` est passée (une fois par minute) | Élevée |
| Compte par téléphone, bon par code, course par `clientRequestId` | Moyenne |
| Bons d'une structure, courses d'un bon | Faible |
| Agrégats de statistiques | Faible |

### 6.7 Rejouer une requête sans la doubler

Sur un réseau faible, l'application abandonne une requête au bout de 15 secondes et propose de
réessayer, alors que le serveur a peut-être déjà enregistré la réservation. Sans précaution :
deux courses, et deux utilisations du bon.

- L'appareil génère un `clientRequestId` (UUID) **une fois par réservation**, et le renvoie tel
  quel à chaque nouvelle tentative.
- `POST /rides` et `POST /operator/rides` cherchent d'abord une course portant cette clé. Si elle
  existe, ils la renvoient sans rien écrire.
- La contrainte d'unicité en base couvre le cas où deux tentatives arrivent en même temps : la
  seconde échoue à l'insertion, l'API relit alors la première.

Les autres écritures sont rejouables par nature : refaire une transition déjà faite par le même
acteur (accepter, démarrer, clôturer, annuler, payer) renvoie la course dans son état actuel, pas
une erreur. Une seconde évaluation renvoie `409`.

### 6.8 Expiration des courses sans chauffeur

Une course `pending` que personne ne prend ne doit pas rester ouverte indéfiniment : elle bloque
une utilisation du bon et laisse l'usager sans réponse.

`expiresAt` est calculée par l'API :

| Situation | `expiresAt` |
|---|---|
| Course immédiate, à la réservation | `createdAt` + 15 minutes |
| Course programmée, à la réservation | `scheduledAt` |
| Après un désistement du chauffeur | Maintenant + 15 minutes, ou `scheduledAt` si c'est plus tard |

Une tâche de l'API tourne chaque minute :

```sql
UPDATE course SET statut = 'expired', expire_le = :maintenant
WHERE statut = 'pending' AND expire_a < :maintenant;
```

puis libère le bon de chaque course expirée ([6.3](#63-consommer-un-bon)), dans la même
transaction. Besoin : un index qui serve cette requête (statut + `expiresAt`).

---

## 7. Hypothèses et questions ouvertes

Choix faits pour pouvoir écrire ce document. Ils ne sont validés ni par le client ni par vous.

**Hypothèses qui touchent le schéma**

| # | Hypothèse | Si elle tombe |
|---|---|---|
| H1 | Connexion par **téléphone** + mot de passe, e-mail facultatif | L'e-mail devient obligatoire et unique |
| H2 | « Usager prioritaire » est un attribut de l'usager, pas un rôle à part | Une valeur de rôle en plus |
| H3 | L'écran opérateur est utilisé par l'administrateur | Un rôle `operator` en plus |
| H4 | Disponibilité du chauffeur = en ligne / hors ligne, pas de planning | Une table de créneaux |
| H5 | Un seul véhicule par chauffeur | Une table véhicule à part, avec un véhicule « actif » |
| H6 | Seule la dernière position du chauffeur est gardée, et effacée hors ligne | Une table d'historique des positions, volumineuse et sensible (RGPD) |
| H7 | Un bon = un pourcentage de prise en charge sur un nombre de courses | Bons en montant (budget en euros), plafond par course… |
| H8 | Un seul tarif (prise en charge + prix au kilomètre) | Grille tarifaire par profil et par type de financement (demandé par le cahier des charges, pas encore classé) |
| H9 | Le chauffeur touche le prix total de la course, sans commission, **même si l'usager n'a pas encore payé** | Un taux de commission, un montant « chauffeur » sur la course, un suivi des versements |
| H10 | Paiement simulé : un simple statut sur la course | Une table de paiements (référence du prestataire, tentatives, remboursements) |
| H11 | Un désistement de chauffeur n'est pas mémorisé (seulement journalisé) | Une table des désistements, ou un compteur sur le chauffeur |
| H12 | Activation et mot de passe oublié par un code généré par un administrateur | Avec de vrais SMS : réinitialisation en libre-service, même stockage du code |
| H13 | Adresses et distance par la route viennent d'un **service externe** appelé par l'API (à choisir, sur données OpenStreetMap). L'usager choisit lui-même la commune dans la liste | Si la commune doit être déduite de la position : les contours des communes en base, avec un type spatial |
| H14 | L'usager peut payer après la course : un impayé n'empêche ni le départ ni la clôture | Paiement exigé avant le départ : pas de changement de schéma, une règle en plus |
| H15 | `isPriority` n'a aucun effet automatique (ni sur le prix, ni sur l'attribution) | Un ordre de priorité dans la recherche de chauffeur, ou un tarif lié au profil (rejoint H8) |

**Questions pour le client** (en plus de celles de `CLAUDE.md`)

1. Un usager qui réserve par téléphone et n'a pas l'application : comment paie-t-il sa part,
   puisque les espèces sont exclues ? Bon à 100 % obligatoire, paiement pris par l'opérateur ?
2. Qu'apporte concrètement le statut d'usager prioritaire (H15) ?
3. Qui supporte un impayé : le chauffeur ou la plateforme (H9, H14) ?
4. Au bout de combien de temps sans chauffeur prévient-on l'usager, et par quel moyen ?
5. Le référent peut-il voir quel usager a utilisé un bon nominatif, ou seulement des totaux ?

**À régler entre développeurs, sans effet sur le schéma**

- Protection contre les requêtes forgées (CSRF) si le jeton est dans un cookie.
- Limitation du nombre d'essais sur `/auth/login`, `/auth/activate` et `/vouchers/check`, tenue
  en mémoire par l'API.
- Hébergement en HTTPS, obligatoire pour la géolocalisation et l'installation de l'application.
- Emplacement de la tâche périodique ([6.8](#68-expiration-des-courses-sans-chauffeur)) et des
  appels au service externe (H13) dans l'architecture.

**Demandé par le cahier des charges, hors de ce contrat pour l'instant** (à trancher avec le
client, mais utile à garder en tête pour ne pas fermer la porte) : notifications à l'usager,
documents des chauffeurs (permis, assurance, agréments), paramétrage des tarifs par
l'administrateur, indicateurs d'impact social, facturation consolidée des partenaires.

**Ce qu'on attend de vous**

1. Le SGBD retenu, et s'il gère les types spatiaux.
2. Le type des identifiants (entier ou UUID).
3. Vos remarques sur ce document : ce qui manque, ce qui est impossible ou coûteux, ce que vous
   modéliseriez autrement.
4. Une date, même approximative, pour une première version du schéma.

Le reste (connexion, données de test, livraison du script) est dans le
[README, partie 5](../README.md#5-pour-léquipe-base-de-données).
