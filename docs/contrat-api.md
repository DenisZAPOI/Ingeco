# Contrat d'API (version 0, proposition)

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
| Dates | ISO 8601 en UTC (`2026-10-13T14:30:00Z`) | Stocker en UTC, avec un type date-heure. La Guyane est en UTC−3 : la conversion est faite à l'affichage |
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
| mot de passe haché | texte (prévoir 255) | non | Jamais en clair. Vide pour un usager créé par téléphone qui n'utilise pas l'application |
| `createdAt` | date-heure | oui | |

Selon le rôle, des informations en plus :

| Rôle | Champ | Type | Obligatoire | Remarques |
|---|---|---|---|---|
| `rider` | `isPriority` | booléen | oui | Usager prioritaire |
| `rider` | `needsAccessibleVehicle` | booléen | oui | Personne à mobilité réduite |
| `driver` | `isAvailable` | booléen | oui | En ligne / hors ligne |
| `driver` | `lastLat`, `lastLng`, `lastLocationAt` | position + date-heure | non | **Dernière position connue seulement**, pas d'historique (RGPD) |
| `driver` | véhicule : `plate`, `model`, `seats`, `isAccessible` | texte, texte, entier, booléen | oui | Un seul véhicule par chauffeur dans le MVP |
| `partner` | `partnerId` | référence | oui | La structure à laquelle le référent appartient |

### 3.2 Structure partenaire (`Partner`)

| Champ | Type | Obligatoire | Remarques |
|---|---|---|---|
| `id` | identifiant | oui | |
| `name` | texte | oui | |
| `type` | `association` \| `collectivity` \| `company` | oui | |
| `status` | `active` \| `suspended` | oui | |

Une structure a un ou plusieurs référents.

### 3.3 Course (`Ride`)

| Champ | Type | Obligatoire | Remarques |
|---|---|---|---|
| `id` | identifiant | oui | |
| `riderId` | référence compte | oui | Le passager |
| `driverId` | référence compte | non | Vide tant qu'aucun chauffeur n'a accepté |
| `bookedById` | référence compte | oui | Qui a saisi la réservation : l'usager lui-même, ou l'opérateur |
| `channel` | `app` \| `phone` | oui | Réservation par l'application ou par téléphone |
| `status` | voir ci-dessous | oui | |
| `purpose` | `employment` \| `training` \| `health` \| `administrative` \| `other` | oui | Motif du trajet, sert aux statistiques |
| `pickupAddress`, `pickupLat`, `pickupLng` | texte + position | oui | Départ |
| `dropoffAddress`, `dropoffLat`, `dropoffLng` | texte + position | oui | Arrivée |
| `pickupCommuneId`, `dropoffCommuneId` | référence commune | oui | Pour les statistiques par commune |
| `scheduledAt` | date-heure | non | Vide = course immédiate |
| `needsAccessibleVehicle` | booléen | oui | Copié du profil de l'usager à la réservation |
| `distanceKm` | décimal | oui | Estimée à la réservation |
| `priceCents` | entier | oui | Prix total, figé à la réservation |
| `voucherId` | référence bon | non | Le bon utilisé, s'il y en a un |
| `voucherAmountCents` | entier | oui | Part payée par le partenaire (0 sans bon) |
| `riderAmountCents` | entier | oui | Part payée par l'usager. `priceCents = voucherAmountCents + riderAmountCents` |
| `paymentStatus` | `not_required` \| `pending` \| `paid` | oui | `not_required` si le bon couvre tout. Paiement simulé dans le MVP |
| `createdAt`, `acceptedAt`, `startedAt`, `completedAt`, `cancelledAt` | date-heure | `createdAt` seulement | Une date par changement d'état |
| `cancelledById` | référence compte | non | |

Cycle de vie de `status` :

```
pending ──▶ accepted ──▶ in_progress ──▶ completed
   │            │
   └────────────┴──▶ cancelled
```

| Statut | Signification |
|---|---|
| `pending` | Réservée, en attente d'un chauffeur |
| `accepted` | Un chauffeur l'a prise |
| `in_progress` | Le passager est à bord |
| `completed` | Terminée |
| `cancelled` | Annulée (possible seulement avant `in_progress`) |

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
| `code` | texte court | oui | **Unique.** Généré par l'API, saisi par l'usager à la réservation |
| `partnerId` | référence structure | oui | Qui finance |
| `issuedById` | référence compte | oui | Le référent qui l'a émis |
| `beneficiaryId` | référence compte | non | Si renseigné, seul cet usager peut l'utiliser |
| `coveragePercent` | entier de 1 à 100 | oui | 100 = prise en charge totale |
| `maxRides` | entier ≥ 1 | oui | Nombre de courses financées |
| `usedRides` | entier ≥ 0 | oui | `usedRides ≤ maxRides` |
| `validFrom`, `validUntil` | date | oui | |
| `status` | `active` \| `revoked` | oui | « Expiré » et « épuisé » se déduisent des dates et du compteur |
| `createdAt` | date-heure | oui | |

**Traçabilité** (exigée par le cahier des charges) : pour chaque course financée, on doit
retrouver le bon, la structure, le montant pris en charge et la date. C'est le rôle de
`voucherId` et `voucherAmountCents` sur la course : ils ne doivent jamais être effacés, même si
le bon est révoqué ensuite.

### 3.6 Données de référence

Fournies par vous, lues par l'API, jamais modifiées par elle dans le MVP.

| Donnée | Contenu | Remarques |
|---|---|---|
| Communes | `id`, `name` | Au minimum les trois communes pilotes : Cayenne, Matoury, Kourou |
| Tarif | `baseFareCents` (prise en charge), `perKmCents` (prix au kilomètre) | Un seul tarif dans le MVP. Prévoir qu'il puisse y en avoir plusieurs plus tard (par profil, par type de financement) |

---

## 4. Les routes

La colonne « En base » résume ce que la route lit (**L**) et écrit (**E**).

### 4.1 Compte et connexion

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `POST /auth/register` | public | Crée un compte `rider` (actif) ou `driver` (en attente, avec son véhicule) | L : téléphone ou e-mail déjà pris ? E : un compte |
| `POST /auth/login` | public | Connexion par téléphone + mot de passe | L : compte par téléphone |
| `POST /auth/logout` | connecté | Déconnexion | Rien |
| `GET /auth/me` | connecté | Renvoie le compte connecté et son profil | L : compte par id |
| `PATCH /users/me` | connecté | Modifie son nom, son e-mail, son mot de passe, ses besoins d'accessibilité | E : le compte |

### 4.2 Réservation (usager)

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `GET /communes` | connecté | Liste des communes desservies | L : communes |
| `POST /vouchers/check` | `rider` | Vérifie un code de bon et renvoie sa prise en charge | L : bon par code |
| `POST /rides/estimate` | `rider`, `admin` | Calcule distance et prix, avec ou sans bon. N'enregistre rien | L : tarif, bon par code |
| `POST /rides` | `rider` | Réserve une course immédiate ou programmée, avec ou sans bon | L : tarif, bon. E : une course, **et** `usedRides + 1` sur le bon, dans la même transaction |
| `GET /rides` | `rider`, `driver` | Ses propres courses, filtrables par `status`, les plus récentes d'abord | L : courses par usager ou par chauffeur |
| `GET /rides/{id}` | participant, `admin` | Détail d'une course, avec le prénom du chauffeur, son véhicule et sa note moyenne | L : course + chauffeur + véhicule + moyenne des évaluations |
| `POST /rides/{id}/cancel` | participant, `admin` | Annule avant le départ | E : statut, et `usedRides − 1` sur le bon s'il y en avait un |
| `POST /rides/{id}/payment` | `rider` de la course | Paiement simulé de la part de l'usager | E : `paymentStatus` |
| `POST /rides/{id}/rating` | `rider` de la course | Évalue une course terminée | E : une évaluation (409 s'il y en a déjà une) |

« Participant » : l'usager ou le chauffeur de la course. Quelqu'un d'autre reçoit `404`.

### 4.3 Chauffeur

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `PUT /drivers/me/availability` | `driver` | Se met en ligne ou hors ligne | E : `isAvailable` |
| `PUT /drivers/me/location` | `driver` | Envoie sa position (toutes les quelques secondes quand il est en ligne) | E : dernière position. **Écriture très fréquente** |
| `GET /drivers/me/ride-offers` | `driver` | Courses en attente proches de lui, compatibles avec son véhicule | L : voir [6.1](#61-trouver-les-chauffeurs-et-les-courses-proches) |
| `POST /rides/{id}/accept` | `driver` | Prend une course en attente | E : voir [6.2](#62-deux-chauffeurs-acceptent-la-même-course) |
| `POST /rides/{id}/start` | `driver` de la course | Passager à bord | E : statut, `startedAt` |
| `POST /rides/{id}/complete` | `driver` de la course | Clôture la course | E : statut, `completedAt` |
| `GET /drivers/me/earnings` | `driver` | Ses revenus sur une période (`?from=&to=`) : total et nombre de courses, par jour | L : somme des `priceCents` de ses courses terminées, groupées par jour |

### 4.4 Bons solidaires (référent partenaire)

Un référent ne voit que les bons de **sa** structure.

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `POST /vouchers` | `partner` | Émet un bon | E : un bon |
| `GET /vouchers` | `partner` | Liste les bons de sa structure, filtrables par état | L : bons par structure |
| `GET /vouchers/{id}` | `partner` | Détail d'un bon et courses qu'il a financées | L : bon + ses courses |
| `POST /vouchers/{id}/revoke` | `partner` | Révoque un bon (les courses déjà réservées restent financées) | E : statut |
| `GET /partners/me/consumption` | `partner` | Suivi sur une période : bons émis, courses financées, montant pris en charge, par mois et par motif | L : agrégats, voir [6.4](#64-statistiques-et-suivi-de-consommation) |

### 4.5 Écran opérateur (réservation par téléphone)

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `GET /operator/riders` | `admin` | Recherche un usager par téléphone ou par nom (`?search=`) | L : recherche sur le téléphone (début) et le nom (contient) |
| `POST /operator/riders` | `admin` | Crée un usager sans mot de passe | E : un compte |
| `POST /operator/rides` | `admin` | Réserve au nom d'un usager | Comme `POST /rides`, avec `channel = phone` et `bookedById` = l'opérateur |

### 4.6 Administration

| Route | Rôle | Ce qu'elle fait | En base |
|---|---|---|---|
| `GET /admin/users` | `admin` | Liste les comptes, filtrables par rôle et statut, recherche par nom ou téléphone | L : comptes |
| `POST /admin/users` | `admin` | Crée un référent partenaire ou un administrateur | E : un compte |
| `PATCH /admin/users/{id}` | `admin` | Valide un chauffeur, suspend ou réactive un compte, marque un usager prioritaire | E : le compte |
| `GET /admin/partners` | `admin` | Liste les structures | L : structures |
| `POST /admin/partners` | `admin` | Crée une structure | E : une structure |
| `PATCH /admin/partners/{id}` | `admin` | Renomme, suspend ou réactive une structure | E : la structure |
| `GET /admin/rides` | `admin` | Toutes les courses, filtrables par statut, date, commune | L : courses |
| `GET /admin/stats` | `admin` | Statistiques sur une période | L : agrégats, voir [6.4](#64-statistiques-et-suivi-de-consommation) |

### 4.7 Exemples de réponses

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
  "voucher": { "id": 7, "code": "SOL-4F7K2Q", "coveragePercent": 50 },
  "driver": {
    "id": 15,
    "firstName": "Prénom",
    "averageScore": 4.7,
    "vehicle": { "plate": "AA-000-AA", "model": "Modèle fictif", "isAccessible": false },
    "location": { "lat": 4.9301, "lng": -52.3255, "updatedAt": "2026-10-13T14:31:10Z" }
  },
  "rating": null,
  "createdAt": "2026-10-13T14:30:00Z",
  "acceptedAt": "2026-10-13T14:30:45Z",
  "startedAt": null,
  "completedAt": null,
  "cancelledAt": null
}
```

Un bon (`GET /vouchers/7`) :

```json
{
  "id": 7,
  "code": "SOL-4F7K2Q",
  "partnerId": 3,
  "beneficiaryId": null,
  "coveragePercent": 50,
  "maxRides": 10,
  "usedRides": 4,
  "validFrom": "2026-10-01",
  "validUntil": "2026-12-31",
  "status": "active",
  "createdAt": "2026-10-01T09:00:00Z"
}
```

---

## 5. Temps réel

Par Socket.IO, un salon par course. **Rien de plus à stocker** : ces événements rediffusent des
données déjà enregistrées par les routes ci-dessus.

| Événement | Envoyé à | Contenu |
|---|---|---|
| `ride:offer` | Chauffeurs en ligne proches | Une nouvelle course en attente |
| `ride:status` | Usager et chauffeur de la course | Le nouveau statut |
| `driver:location` | Usager de la course, tant qu'elle est `accepted` ou `in_progress` | La position du chauffeur |

Les SMS du mode dégradé sont simulés (écrits dans les logs) : pas de table pour le MVP.

---

## 6. Les requêtes qui demandent de l'attention

Les points où le schéma (types, index, contraintes) change vraiment la difficulté du code.

### 6.1 Trouver les chauffeurs et les courses proches

- À la réservation : les chauffeurs `active`, `isAvailable`, avec une position récente (moins de
  quelques minutes), sans course `accepted` ou `in_progress`, avec un véhicule accessible si la
  course le demande, **triés par distance** au point de départ.
- Pour `GET /drivers/me/ride-offers` : l'inverse, les courses `pending` dont le départ est dans
  un rayon donné autour du chauffeur.

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

### 6.3 Consommer un bon

Réserver une course avec un bon fait deux écritures dans **une** transaction : créer la course et
incrémenter `usedRides`. Même principe que ci-dessus pour ne jamais dépasser le plafond :

```sql
UPDATE bon SET courses_utilisees = courses_utilisees + 1
WHERE id = :bon AND statut = 'active' AND courses_utilisees < courses_max
  AND :aujourdhui BETWEEN valide_du AND valide_au;
```

Une contrainte `CHECK (courses_utilisees <= courses_max)` en base serait une sécurité bienvenue.

### 6.4 Statistiques et suivi de consommation

Toutes sur une période (`from`, `to`), calculées à la demande (pas de table d'agrégats pour le
volume du MVP, quelques dizaines de courses par jour) :

- nombre de courses par statut, par jour, par commune de départ, par motif, par canal ;
- nombre d'usagers et de chauffeurs actifs ;
- nombre de courses financées et montant pris en charge, au total et par structure ;
- note moyenne (objectif du client : plus de 90 % de satisfaction) ;
- pour un référent : les mêmes chiffres, limités à sa structure.

Besoin : des index sur les dates et les statuts des courses, et des valeurs de statut, de motif
et de commune **contraintes** (clé étrangère ou `CHECK`), sinon les regroupements seront faux.

### 6.5 Unicité et intégrité

| Règle | Où |
|---|---|
| Téléphone unique ; e-mail unique s'il est renseigné | Compte |
| Code unique | Bon |
| Une évaluation au plus par course | Évaluation |
| `priceCents = voucherAmountCents + riderAmountCents`, montants ≥ 0 | Course |
| `score` entre 1 et 5, `coveragePercent` entre 1 et 100 | Évaluation, bon |
| Un chauffeur n'a qu'une course `accepted` ou `in_progress` à la fois | Course (vérifié par l'API, une contrainte en base si votre SGBD le permet) |

### 6.6 Accès les plus fréquents (pour vos index)

| Accès | Fréquence |
|---|---|
| Compte par id (à chaque requête authentifiée) | Très élevée |
| Mise à jour de la position d'un chauffeur | Très élevée |
| Course par id | Élevée |
| Courses d'un usager / d'un chauffeur, triées par date | Élevée |
| Courses par statut (`pending` surtout) | Élevée |
| Compte par téléphone, bon par code | Moyenne |
| Bons d'une structure, courses d'un bon | Faible |
| Agrégats de statistiques | Faible |

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
| H6 | Seule la dernière position du chauffeur est gardée | Une table d'historique des positions, volumineuse et sensible (RGPD) |
| H7 | Un bon = un pourcentage de prise en charge sur un nombre de courses | Bons en montant (budget en euros), plafond par course… |
| H8 | Un seul tarif (prise en charge + prix au kilomètre) | Grille tarifaire par profil et par type de financement (demandé par le cahier des charges, pas encore classé) |
| H9 | Le chauffeur touche le prix total de la course, sans commission | Un taux de commission et un montant « chauffeur » sur la course |
| H10 | Paiement simulé : un simple statut sur la course | Une table de paiements (référence du prestataire, tentatives) |

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
