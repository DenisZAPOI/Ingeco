# Contrat d'API (version 2, proposition)

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

## Ce qui change depuis la version 1

Le client a répondu le 13/10/2026 à une partie de nos questions
([points-a-valider-porteur.pdf](points-a-valider-porteur.pdf)). Trois réponses changent le
contrat : le paiement se fait **à la réservation, avant le trajet**, par carte uniquement ; le
centre d'appel est tenu par **des personnes dédiées** ; tout le monde peut réserver par téléphone.
La numérotation n'a pas bougé, les ajouts sont en fin de partie (6.9, H16, H17). Le détail du
raisonnement est dans [cas-d-utilisation.md](cas-d-utilisation.md).

| Sujet | Changement | Effet sur le schéma |
|---|---|---|
| Paiement avant le trajet | Nouveau statut `awaiting_payment` : la course n'est proposée aux chauffeurs qu'une fois payée ([3.3](#33-course-ride)). La notion d'impayé disparaît | Une valeur de statut |
| Course qui expire | Rembourse la part payée ([6.8](#68-expiration-des-courses-sans-chauffeur)). Un délai de paiement de 15 minutes s'ajoute | Aucun |
| Centre d'appel | Nouveau rôle `operator`, sans droits d'administration ([2](#2-rôles)) | Une valeur de rôle |
| Paiement par téléphone | L'opérateur n'enregistre plus le paiement : l'usager reçoit un lien de paiement par SMS ([6.9](#69-lien-de-paiement-par-sms)) | Aucun (lien signé, rien à stocker) |
| Opérateur | Consulte les courses d'un usager (`GET /operator/riders/{id}/rides`) | Aucun |
| Statistiques | Les impayés sont remplacés par les paiements abandonnés ([6.4](#64-statistiques-et-suivi-de-consommation)) | Aucun |
| Intégrité | Une course proposée aux chauffeurs est toujours payée ou sans part usager ([6.5](#65-unicité-et-intégrité)) | Une contrainte possible |
| Comptes chauffeurs (décision du 19/10/2026) | Plus d'inscription chauffeur en ligne : il apporte ses documents en personne, puis un administrateur crée son compte avec son véhicule, et le chauffeur l'active avec un code. `POST /auth/register` ne crée que des usagers | La valeur de statut `pending` du compte disparaît |
| Session | Routes `POST /auth/refresh` et code `429`, règles du mot de passe et du téléphone ([4.1](#41-compte-et-connexion)) | Aucun |

### Changements de la version 0 à la version 1

La version 0 a été relue : elle laissait des cas sans réponse. Les ajouts étaient en fin de
partie (6.7, 6.8, H11 à H15).

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
métier violée, `429` trop d'essais. Le détail est dans [architecture.md](architecture.md#contrat-dapi).

---

## 2. Rôles

Chaque compte a **un** rôle.

| Rôle (valeur dans l'API) | Profil | Créé par |
|---|---|---|
| `rider` | Usager, prioritaire ou non (attribut `isPriority`) | Lui-même, ou un opérateur par téléphone |
| `driver` | Chauffeur | Un administrateur, après vérification des documents en personne |
| `partner` | Référent d'une structure partenaire | Un administrateur |
| `operator` | Opérateur du centre d'appel : retrouve, crée un usager, réserve et annule à sa place. Aucun droit d'administration (H3) | Un administrateur |
| `admin` | Administrateur. Peut aussi utiliser l'écran opérateur, pour remplacer un opérateur | Un administrateur |

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
| `role` | `rider` \| `driver` \| `partner` \| `operator` \| `admin` | oui | |
| `status` | `active` \| `suspended` | oui | Un compte pas encore activé est `active` sans mot de passe |
| `firstName`, `lastName` | texte | oui | |
| `phone` | texte | oui | **Unique.** Sert d'identifiant de connexion. Format international (`+594…`) |
| `email` | texte | non | Unique s'il est renseigné |
| mot de passe haché | texte (prévoir 255) | non | Jamais en clair. Vide tant que le compte n'est pas activé |
| code d'activation haché | texte (prévoir 255) | non | Jamais en clair. Vide hors période d'activation |
| `activationCodeExpiresAt` | date-heure | non | Fin de validité du code (48 h après sa création) |
| `createdAt` | date-heure | oui | |

**Activation.** Un compte créé par quelqu'un d'autre (usager créé par l'opérateur, chauffeur,
référent, opérateur, administrateur) n'a pas de mot de passe. Un administrateur génère un code à usage unique, le
transmet à la personne (par téléphone ou en main propre), et celle-ci choisit son mot de passe
avec `POST /auth/activate`. Le même mécanisme sert au mot de passe oublié : pas de
réinitialisation en libre-service tant que les SMS sont simulés (H12). Le code fait 8 chiffres,
facile à dicter.

**Session.** Deux JWT dans des cookies `HttpOnly` : un jeton d'accès de 15 minutes et un jeton de
renouvellement de 30 jours. Protection CSRF par double envoi : un cookie lisible porte un jeton
que le front recopie dans l'en-tête `X-CSRF-TOKEN` de chaque écriture. Rien à stocker en base.

**Saisie.** Le téléphone est saisi comme l'usager le connaît (`0694 12 34 56`) et enregistré au
format international (`+594694123456`). Mot de passe : au moins 8 caractères, dont une
majuscule, un chiffre et un symbole. Un usager créé par
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
| `expiresAt` | date-heure | oui | Échéance au-delà de laquelle une course encore `awaiting_payment` ou `pending` expire, voir [6.8](#68-expiration-des-courses-sans-chauffeur). Recalculée au paiement |
| `createdAt`, `acceptedAt`, `startedAt`, `completedAt`, `cancelledAt`, `expiredAt`, `paidAt` | date-heure | `createdAt` seulement | Une date par changement d'état. `acceptedAt` est remise à vide si le chauffeur se désiste |
| `cancelledById` | référence compte | non | |

Cycle de vie de `status` :

```
                                       ┌──── désistement ────┐
                                       ▼                     │
  awaiting_payment ──paiement──▶  pending ──────────▶ accepted ──▶ in_progress ──▶ completed

  awaiting_payment, pending            ──▶ expired     (délai dépassé)
  awaiting_payment, pending, accepted  ──▶ cancelled   (annulation avant le départ)
```

Une réservation sans part à payer (bon à 100 %) est créée directement en `pending`.

| Statut | Signification | Qui déclenche |
|---|---|---|
| `awaiting_payment` | Réservée, en attente du paiement de la part de l'usager. **Pas encore proposée aux chauffeurs** | L'usager ou l'opérateur (réservation) |
| `pending` | Payée (ou rien à payer), en attente d'un chauffeur | Le paiement, la réservation si rien à payer, le chauffeur (désistement) |
| `accepted` | Un chauffeur l'a prise | Un chauffeur |
| `in_progress` | Le passager est à bord | Le chauffeur de la course |
| `completed` | Terminée | Le chauffeur de la course |
| `cancelled` | Annulée avant `in_progress` | L'usager de la course, un opérateur, un administrateur |
| `expired` | Pas payée à temps, ou aucun chauffeur ne l'a prise à temps | L'API, automatiquement |

**Course active d'un chauffeur.** Une course `in_progress`, ou une course `accepted` qui est
immédiate ou dont `scheduledAt` tombe dans les 60 prochaines minutes. Un chauffeur n'a qu'**une**
course active à la fois, mais il peut avoir accepté plusieurs courses programmées à l'avance, à
condition qu'elles soient espacées d'au moins 60 minutes. Les durées de ce document (60 minutes,
30 minutes, 15 minutes, 48 heures) sont des réglages de l'API, pas des données : rien à stocker.

**Paiement** (simulé dans le MVP, H10). Confirmé par le client : **carte bancaire uniquement, à
la réservation, avant le trajet**.

- `not_required` : le bon couvre tout (`riderAmountCents = 0`). La course naît en `pending`.
- `pending` → `paid` : la course est en `awaiting_payment`. L'usager paie sa part dans
  l'application, ou par le lien reçu par SMS s'il a réservé par téléphone
  ([6.9](#69-lien-de-paiement-par-sms)). Le paiement fait passer la course en `pending`, et
  c'est seulement alors qu'elle est proposée aux chauffeurs.
- Paiement refusé : rien ne change, l'usager peut réessayer jusqu'à `expiresAt`.
- `paid` → `refunded` : la course est annulée ou expire après le paiement. Remboursement intégral
  dans tous les cas (H17).
- Une course `accepted`, `in_progress` ou `completed` est donc toujours `paid` ou
  `not_required` : il n'y a plus d'impayé.
- L'opérateur n'enregistre jamais de paiement et ne voit jamais de numéro de carte.

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
| `POST /auth/register` | public | Crée un compte `rider` actif et ouvre la session. Jamais un autre rôle. `409` si le téléphone existe déjà, y compris pour un compte créé par l'opérateur : il faut alors l'activer | L : téléphone ou e-mail déjà pris ? E : un compte |
| `POST /auth/activate` | public | Téléphone + code d'activation + nouveau mot de passe, puis ouvre la session. Efface le code. `422` si le code est faux ou expiré, `429` après 5 échecs en 15 minutes | L : compte par téléphone. E : mot de passe, code remis à vide |
| `POST /auth/login` | public | Connexion par téléphone + mot de passe. `429` après 5 échecs en 15 minutes pour le même numéro | L : compte par téléphone |
| `POST /auth/refresh` | connecté | Renouvelle le jeton d'accès (15 min) à partir du jeton de renouvellement (30 jours). Relit le compte : un compte suspendu est déconnecté ici | L : compte par id |
| `POST /auth/logout` | public | Efface les cookies de session | Rien |
| `GET /auth/me` | connecté | Renvoie le compte connecté et son profil | L : compte par id |
| `PATCH /users/me` | connecté | Modifie son nom, son e-mail, son mot de passe, ses besoins d'accessibilité | E : le compte |

### 4.2 Réservation (usager)

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `GET /communes` | connecté | Liste des communes desservies | L : communes |
| `GET /places` | connecté | Cherche une adresse dans une commune (`?search=&communeId=`) et renvoie des propositions avec leur position | Rien (service externe, H13) |
| `POST /vouchers/check` | `rider`, `operator`, `admin` | Vérifie un code de bon et renvoie sa prise en charge. L'opérateur précise le `riderId` | L : bon par code, structure |
| `POST /rides/estimate` | `rider`, `operator`, `admin` | Calcule distance et prix, avec ou sans bon. N'enregistre rien. L'opérateur précise le `riderId` | L : tarif, bon par code |
| `POST /rides` | `rider` | Réserve une course immédiate ou programmée, avec ou sans bon. Recalcule le prix : celui de l'estimation n'est jamais repris tel quel. Crée la course en `awaiting_payment`, ou en `pending` si la part usager est nulle | L : tarif, bon, course par `clientRequestId`. E : une course, **et** `usedRides + 1` sur le bon, dans la même transaction |
| `GET /rides` | `rider`, `driver` | Ses propres courses, filtrables par `status`, les plus récentes d'abord | L : courses par usager ou par chauffeur |
| `GET /rides/{id}` | participant, `operator`, `admin` | Détail d'une course, avec le prénom du chauffeur, son véhicule et sa note moyenne. La position du chauffeur n'est renvoyée que si la course est active | L : course + chauffeur + véhicule + moyenne des évaluations |
| `POST /rides/{id}/cancel` | `rider` de la course, `operator`, `admin` | Annule une course `awaiting_payment`, `pending` ou `accepted` | E : statut, `usedRides − 1` sur le bon s'il y en avait un, `paymentStatus = refunded` si elle était payée |
| `POST /rides/{id}/payment` | `rider` de la course | Paiement simulé de la part de l'usager, sur une course `awaiting_payment`. La fait passer en `pending` et la propose aux chauffeurs | E : `paymentStatus`, `paidAt`, statut, nouvelle `expiresAt` |
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
| `GET /operator/riders` | `operator`, `admin` | Recherche un usager par téléphone ou par nom (`?search=`) | L : recherche sur le téléphone (début) et le nom (contient) |
| `POST /operator/riders` | `operator`, `admin` | Crée un usager sans mot de passe | E : un compte |
| `GET /operator/riders/{id}/rides` | `operator`, `admin` | Courses d'un usager : à venir d'abord, puis passées. Sert à répondre à l'appel et à retrouver une course à annuler (Q2 du client, à confirmer) | L : courses par usager |
| `POST /operator/rides` | `operator`, `admin` | Réserve au nom d'un usager. Si une part reste à payer, envoie le lien de paiement par SMS | Comme `POST /rides`, avec `channel = phone` et `bookedById` = l'opérateur |
| `POST /operator/rides/{id}/payment-link` | `operator`, `admin` | Renvoie le lien de paiement (SMS perdu, usager qui rappelle). Seulement sur une course `awaiting_payment` | L : course, téléphone de l'usager. E : rien, voir [6.9](#69-lien-de-paiement-par-sms) |

L'opérateur vérifie un bon, estime un prix, consulte et annule une course avec les routes de la
partie 4.2, qui acceptent le rôle `operator`. Il n'a accès à aucune route de la partie 4.6.

Le paiement par lien se fait sur deux routes publiques, protégées par le jeton du lien :

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `GET /payment-links/{token}` | public (jeton) | Ce qu'il y a à payer : montant, communes, horaire. Ni nom, ni adresse | L : course |
| `POST /payment-links/{token}` | public (jeton) | Paiement simulé, même effet que `POST /rides/{id}/payment` | E : comme `POST /rides/{id}/payment` |

### 4.6 Administration

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `GET /admin/users` | `admin` | Liste les comptes, filtrables par rôle et statut, recherche par nom ou téléphone | L : comptes |
| `POST /admin/users` | `admin` | Crée un chauffeur (avec son véhicule, après vérification de ses documents en personne), un référent partenaire, un opérateur ou un administrateur, sans mot de passe | E : un compte |
| `PATCH /admin/users/{id}` | `admin` | Suspend ou réactive un compte, marque un usager prioritaire, modifie le véhicule d'un chauffeur | E : le compte |
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
  "paymentStatus": "paid",
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
  "paidAt": "2026-10-13T14:30:20Z",
  "expiresAt": "2026-10-13T14:45:20Z",
  "acceptedAt": "2026-10-13T14:30:45Z",
  "startedAt": null,
  "completedAt": null,
  "cancelledAt": null,
  "expiredAt": null
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
| `ride:offer` | `driver:{id}` de chaque chauffeur en ligne proche | Une nouvelle course immédiate à prendre (quand elle passe en `pending` : après le paiement, à la réservation si rien à payer, ou après un désistement) |
| `ride:offer-closed` | Les mêmes | La course n'est plus à prendre (acceptée, annulée ou expirée) |
| `ride:updated` | `ride:{id}` | La course complète, après chaque changement d'état |
| `driver:location` | `ride:{id}`, tant que la course est active | La position du chauffeur |

Un événement perdu n'est pas renvoyé. À chaque reconnexion, le front relit l'état par les routes
HTTP (`GET /rides/{id}`, `GET /drivers/me/ride-offers`) : le temps réel accélère l'affichage, il
n'est jamais la seule source.

Les SMS (mode dégradé, lien de paiement) sont simulés (écrits dans les logs, sans numéro ni
contenu personnel) : pas de table pour le MVP.

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
- nombre de courses `expired` faute de chauffeur (`paymentStatus` à `refunded` ou
  `not_required`) : c'est la demande que le service n'a pas su servir ;
- nombre de courses `expired` faute de paiement (`paymentStatus` resté à `pending`) : les
  paiements abandonnés ;
- nombre d'usagers et de chauffeurs actifs, part des usagers prioritaires ;
- nombre de courses financées et montant pris en charge, au total et par structure ;
- nombre et montant des remboursements ;
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
| Statut `pending`, `accepted`, `in_progress` ou `completed` ⇒ `paymentStatus` à `paid` ou `not_required` | Course |
| Un chauffeur n'a qu'une course active à la fois, et ses courses programmées sont espacées d'au moins 60 minutes | Course. **Vérifié par l'API seulement** : la règle dépend de l'heure, une contrainte en base ne peut pas l'exprimer |

### 6.6 Accès les plus fréquents (pour vos index)

| Accès | Fréquence |
|---|---|
| Compte par id (à chaque requête authentifiée) | Très élevée |
| Mise à jour de la position d'un chauffeur | Très élevée |
| Course par id | Élevée |
| Courses d'un usager / d'un chauffeur, triées par date | Élevée |
| Courses par statut (`pending` surtout) | Élevée |
| Courses `awaiting_payment` ou `pending` dont `expiresAt` est passée (une fois par minute) | Élevée |
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

Une course `pending` que personne ne prend, ou `awaiting_payment` que personne ne paie, ne doit
pas rester ouverte indéfiniment : elle bloque une utilisation du bon et laisse l'usager sans
réponse.

`expiresAt` est calculée par l'API :

| Situation | `expiresAt` |
|---|---|
| Réservation avec une part à payer (`awaiting_payment`) | `createdAt` + 15 minutes (délai de paiement, H16) |
| Course immédiate, quand elle passe en `pending` (paiement, ou réservation sans part à payer) | Maintenant + 15 minutes |
| Course programmée, quand elle passe en `pending` | `scheduledAt` |
| Après un désistement du chauffeur | Maintenant + 15 minutes, ou `scheduledAt` si c'est plus tard |

Le délai de paiement (15 minutes) est plus court que le délai minimal d'une course programmée
(30 minutes) : une course programmée payée à temps est toujours encore à venir.

Une tâche de l'API tourne chaque minute :

```sql
UPDATE course SET statut = 'expired', expire_le = :maintenant
WHERE statut IN ('awaiting_payment', 'pending') AND expire_a < :maintenant;
```

puis, dans la même transaction, libère le bon de chaque course expirée
([6.3](#63-consommer-un-bon)) et passe en `refunded` celles qui étaient `paid`. L'usager est
prévenu (SMS simulé) et peut refaire sa demande. Le remboursement est simulé dans le MVP ; avec un
vrai prestataire, l'appel de remboursement se fera après la transaction, avec nouvelle tentative
en cas d'échec. Besoin : un index qui serve cette requête (statut + `expiresAt`).

### 6.9 Lien de paiement par SMS

Un usager qui réserve par téléphone paie sa part sur son propre téléphone : l'opérateur ne voit
jamais de numéro de carte (sinon le centre d'appel devrait appliquer les règles de sécurité des
cartes bancaires).

- À la réservation (`POST /operator/rides`), l'API envoie à l'usager un SMS contenant un lien
  `/payer/{token}`. Simulé dans le MVP : une ligne de log sans numéro ni contenu personnel, et le
  lien est affiché à l'opérateur pour les démonstrations.
- Le jeton est **signé** par l'API avec sa clé secrète : il contient l'identifiant de la course
  et une échéance égale à `expiresAt`. **Rien à stocker en base.**
- Il est à usage unique par construction : le paiement ne réussit que sur une course
  `awaiting_payment` (mise à jour conditionnelle, comme en [6.2](#62-deux-chauffeurs-acceptent-la-même-course)).
  Un lien déjà utilisé affiche « Déjà payé ».
- Le jeton ne doit jamais apparaître dans les logs : `utils/request_logs.py` journalise le chemin
  de chaque requête, il faudra y masquer la partie `{token}`.
- La page de paiement ne montre ni le nom, ni les adresses : seulement le montant, les communes et
  l'horaire. Quelqu'un qui intercepte le lien ne peut que payer la course à la place de l'usager.
- Un usager sans téléphone capable d'ouvrir un lien ne peut voyager qu'avec un bon à 100 %
  (question 1 ci-dessous).

---

## 7. Hypothèses et questions ouvertes

Choix faits pour pouvoir écrire ce document. Ils ne sont validés ni par le client ni par vous.

**Hypothèses qui touchent le schéma**

| # | Hypothèse | Si elle tombe |
|---|---|---|
| H1 | Connexion par **téléphone** + mot de passe, e-mail facultatif | L'e-mail devient obligatoire et unique |
| H2 | « Usager prioritaire » est un attribut de l'usager, pas un rôle à part | Une valeur de rôle en plus |
| H3 | Le centre d'appel est tenu par des personnes dédiées (confirmé par le client), qui ont un rôle `operator` à part, sans droits d'administration | Si elles doivent tout pouvoir faire : le rôle `admin`, une valeur de rôle en moins |
| H4 | Disponibilité du chauffeur = en ligne / hors ligne, pas de planning | Une table de créneaux |
| H5 | Un seul véhicule par chauffeur | Une table véhicule à part, avec un véhicule « actif » |
| H6 | Seule la dernière position du chauffeur est gardée, et effacée hors ligne | Une table d'historique des positions, volumineuse et sensible (RGPD) |
| H7 | Un bon = un pourcentage de prise en charge sur un nombre de courses | Bons en montant (budget en euros), plafond par course… |
| H8 | Un seul tarif (prise en charge + prix au kilomètre) | Grille tarifaire par profil et par type de financement (demandé par le cahier des charges, pas encore classé) |
| H9 | Le chauffeur touche le prix total de la course, sans commission | Un taux de commission, un montant « chauffeur » sur la course, un suivi des versements |
| H10 | Paiement simulé : un simple statut sur la course | Une table de paiements (référence du prestataire, tentatives, remboursements) |
| H11 | Un désistement de chauffeur n'est pas mémorisé (seulement journalisé) | Une table des désistements, ou un compteur sur le chauffeur |
| H12 | Activation et mot de passe oublié par un code généré par un administrateur | Avec de vrais SMS : réinitialisation en libre-service, même stockage du code |
| H13 | Adresses et distance par la route viennent d'un **service externe** appelé par l'API (à choisir, sur données OpenStreetMap). L'usager choisit lui-même la commune dans la liste | Si la commune doit être déduite de la position : les contours des communes en base, avec un type spatial |
| H14 | Par téléphone, l'usager paie par un lien reçu par SMS ([6.9](#69-lien-de-paiement-par-sms)) | Carte dictée à l'opérateur : règles de sécurité des cartes bancaires au centre d'appel, déconseillé. Sans effet sur le schéma |
| H15 | `isPriority` n'a aucun effet automatique (ni sur le prix, ni sur l'attribution) | Un ordre de priorité dans la recherche de chauffeur, ou un tarif lié au profil (rejoint H8) |
| H16 | 15 minutes pour payer, sinon la réservation expire et le bon est rendu | Un autre délai : aucun effet sur le schéma |
| H17 | Remboursement intégral en cas d'annulation ou d'expiration, quels que soient l'auteur et le moment | Frais d'annulation tardive : un montant remboursé sur la course |

**Questions pour le client** (en plus de celles de `CLAUDE.md`)

1. Le lien de paiement par SMS convient-il (H14) ? Un usager dont le téléphone ne peut pas ouvrir
   de lien ne pourra voyager qu'avec un bon à 100 % : est-ce acceptable ?
2. Qu'apporte concrètement le statut d'usager prioritaire (H15) ?
3. L'opérateur peut-il consulter les trajets d'un usager (`GET /operator/riders/{id}/rides`) ?
4. Au bout de combien de temps sans chauffeur prévient-on l'usager, et par quel moyen ?
5. Le référent peut-il voir quel usager a utilisé un bon nominatif, ou seulement des totaux ?
6. Le remboursement est-il intégral dans tous les cas (H17) ?

**À régler entre développeurs, sans effet sur le schéma**

- Limitation du nombre d'essais sur `/vouchers/check` et `/payment-links/{token}`, comme pour
  `/auth/login` et `/auth/activate` (déjà en place).
- Hébergement en HTTPS, obligatoire pour la géolocalisation, l'installation de l'application et
  les cookies de session (`COOKIE_SECURE=true`). Le front et l'API doivent être servis sous le même
  site (même domaine parent), sinon le front ne peut pas lire le cookie CSRF.
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
