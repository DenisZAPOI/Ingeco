# Décisions et valeurs provisoires

Ce document est **la référence pour la suite du développement** : il dit ce qui est décidé, et
quelle valeur provisoire on applique à tout ce qui ne l'est pas encore. Il complète
[points-a-valider-porteur.pdf](points-a-valider-porteur.pdf) (questions Q1 à Q15, propositions
A à F) et les hypothèses H1 à H19 de [contrat-api.md](contrat-api.md#7-hypothèses-et-questions-ouvertes).

- **Première version** : 03/11/2026, réponses transmises par Denis ZAPOI.
- **À tenir à jour** : à chaque réponse du client, déplacer le point de la partie 3 vers la
  partie 2, puis mettre à jour le code et les autres documents (partie 4).

## Sommaire

1. [Règle des valeurs provisoires](#1-règle-des-valeurs-provisoires)
2. [Ce qui est décidé](#2-ce-qui-est-décidé)
3. [Ce qui n'est pas décidé : valeurs provisoires](#3-ce-qui-nest-pas-décidé--valeurs-provisoires)
4. [Ce que ces décisions changent](#4-ce-que-ces-décisions-changent)

---

## 1. Règle des valeurs provisoires

On n'attend plus une réponse pour avancer. Tout point **non décidé** reçoit une valeur
provisoire (en général l'hypothèse déjà proposée au client), et cette valeur est **repérable**
pour être changée en un seul endroit le jour où la décision tombe :

- **Dans le code** : une constante nommée, précédée du commentaire `CHANGER_SELON_DECISION`, avec
  la référence du point (Q8, H18…). Un `grep CHANGER_SELON_DECISION` donne la liste de tout ce
  qui reste à trancher.

  ```python
  # CHANGER_SELON_DECISION (Q8, H9) : commission de la plateforme, voir docs/decisions.md.
  PLATFORM_COMMISSION_RATE = Decimal("0.10")
  ```

  ```ts
  // CHANGER_SELON_DECISION (Q8) : voir docs/decisions.md.
  ```

- **Dans la documentation** : la mention `CHANGER_SELON_DECISION` à côté de la valeur.
- **Une valeur stockée en base** (le tarif, par exemple) se signale de la même façon dans
  `sql/schema-mvp.sql`, en commentaire SQL (`-- CHANGER_SELON_DECISION`), et la modification
  passe par l'équipe BD.

Une valeur provisoire reste une hypothèse : on ne construit pas dessus un écran ou une table
qu'il faudrait jeter si la réponse était différente.

---

## 2. Ce qui est décidé

| # | Sujet | Décision | Conséquence |
|---|---|---|---|
| Q1, H14 | Paiement d'une réservation par téléphone | **Lien de paiement envoyé par SMS** (simulé en MVP). La carte dictée à l'opérateur est écartée : elle impose trop de contraintes de sécurité au centre d'appel | UC45 passe de « à trancher » à **MVP simulé** (étape 6). Contrat [6.9](contrat-api.md#69-lien-de-paiement-par-sms) confirmé |
| Q2 (en partie) | Droits de l'opérateur | L'opérateur **peut créer un compte à la place de l'usager**, en plus de réserver | UC41 confirmé (étape 6). Annuler et consulter les trajets passés : voir partie 3 |
| Q15 | Tableau de bord administrateur | **Libre** : le contenu est au choix de l'équipe | UC56 (étape 7) n'attend plus de réponse. Point de départ : l'hypothèse de Q15 (trajets par jour, par commune et par motif, trajets financés et montants, note moyenne) |
| Q10, H8 | Montants du tarif | **On garde le tarif provisoire** : 8 € de prise en charge + 0,80 €/km | Rien à changer : déjà dans `sql/schema-mvp.sql` et les données factices. Reste marqué `CHANGER_SELON_DECISION` tant que le client ne donne pas les montants définitifs |
| Q8, H9 | Commission de la plateforme | **Un taux provisoire dans une constante**, marqué `CHANGER_SELON_DECISION` : **10 %** (chiffre arbitraire, à remplacer) | Les revenus du chauffeur (UC28) deviennent « prix − commission ». À faire : voir partie 4 |
| H19 | Profil du chauffeur montré au passager (« mini CV ») | **Prénom, note moyenne et photo**. Rien d'autre | Déjà renvoyé par l'API (`firstName`, `averageScore`, `GET /rides/{id}/driver-photo`). La photo reste à afficher sur la page du trajet (étape 4). Aucun champ de profil en plus en base |
| – | Numéros de téléphone entre usager et chauffeur | **Oui, partagés pendant la course**, pour qu'ils puissent s'appeler à la prise en charge | Déjà fait : le numéro n'est renvoyé que pendant une course acceptée ou en cours. Différence avec Uber : Uber masque le vrai numéro derrière un numéro relais ; ici le vrai numéro est montré, seulement pendant la course |
| H18 | Zone du pilote | **Celle donnée en visio** ([compte-rendu-visio-1.md](compte-rendu-visio-1.md)) : Cayenne et environ 5 km autour, avec Rémire-Montjoly et Matoury (Cogneau-Lamirande). Départ et arrivée doivent être dans l'une de ces 3 communes | Déjà la règle de l'API (liste des communes). Le rayon de contrôle et la réponse hors zone restent provisoires : voir partie 3 |

---

## 3. Ce qui n'est pas décidé : valeurs provisoires

Chaque ligne s'applique telle quelle jusqu'à la réponse du client. « Où » indique l'endroit à
modifier le jour où la décision tombe.

### Centre d'appel et usagers

| # | Sujet | Valeur provisoire | Où |
|---|---|---|---|
| Q2 | L'opérateur peut-il annuler pour un usager ? | Oui (UC43, hypothèse déjà proposée) | Droits de `POST /rides/{id}/cancel` |
| Q2, UC44 | L'opérateur peut-il consulter les trajets passés d'un usager ? | Non : pas de route `GET /operator/riders/{id}/rides` tant que ce n'est pas demandé (données sensibles, dont le motif) | Étape 6 |
| H3 | Qui tient le centre d'appel | Des personnes dédiées, rôle `operator` sans droits d'administration (confirmé le 13/10/2026, trace écrite à retrouver) | Rôle `operator` |
| Q3 | Qui attribue le statut d'usager prioritaire | L'administrateur (déjà en place, UC51) | `PATCH /admin/users/{id}` |
| Q4, H15 | Ce qu'apporte ce statut | Aucun effet automatique (ni prix, ni attribution) | Services de réservation et d'attribution |

### Bons solidaires (étape 5)

| # | Sujet | Valeur provisoire | Où |
|---|---|---|---|
| Q5, H7 | Forme d'un bon | Un pourcentage de prise en charge sur un nombre de trajets (ex. 50 % sur 10 trajets) | `sql/schema-hors-scope.sql`, demande à l'équipe BD |
| Q6 | Bon nominatif ou code libre | Les deux possibles | Idem |
| Q9 | Usager sans carte bancaire | Il ne voyage qu'avec un bon à 100 % | Réservation (UC13) |
| Q12 | Ce que voit la structure qui finance | Date, communes et montant de chaque trajet ; ni nom, ni adresse, ni motif | `GET /partners/me/consumption` |
| H16 | Bon rendu si la réservation expire | Oui | Expiration (UC60) |

Les bons sont le seul bloc qui demande des **tables nouvelles** : tant que Q5 et Q6 ne sont pas
tranchés, on ne demande pas à l'équipe BD de les créer (règle de la partie 1 : pas de table
construite sur une valeur provisoire). Si aucune réponse n'arrive d'ici fin novembre 2026, il
faudra décider avec le client de sortir les bons du MVP ou de les livrer sur ces valeurs.

### Courses, paiement, annulation

| # | Sujet | Valeur provisoire | Où |
|---|---|---|---|
| A | Horaires | Demandes acceptées à toute heure ; le service tourne quand des chauffeurs sont en ligne | Aucun code |
| – | « 24h/24 » ou « semaine avec créneaux élargis » | Idem A : aucune restriction d'horaire dans l'application | Aucun code |
| B | Prix | Prise en charge + prix au km, annoncé avant paiement, figé ensuite (déjà en place) | `ride_rules.price_cents` |
| C, H8 | Tarif unique | Même tarif pour tous ; la solidarité passe par les bons | Table `tarif` |
| D, H16 | Aucun chauffeur trouvé | Recherche pendant 15 min, puis expiration, remboursement, nouvelle demande possible (déjà en place, UC60) | Constantes de l'expiration |
| H16 | Délai pour payer | 15 min, sinon la réservation expire | Idem |
| E, H11 | Chauffeur qui se désiste | Course reproposée aux autres chauffeurs, sans nouvelle demande ni nouveau paiement (déjà en place, UC24) | Service des courses |
| F | Satisfaction | Note de 1 à 5 ; taux de satisfaction = part des notes 4 ou 5, objectif 90 % | Statistiques (étape 7) |
| Q7, H17 | Remboursement | Intégral dans tous les cas, quel que soit l'auteur ou le moment | Annulation (UC16) |
| H10 | Paiement | Simulé : un statut sur la course, pas de prestataire réel. Une table des paiements sera demandée à l'équipe BD si on branche le mode test d'un prestataire | Service de paiement |

### Zone

| # | Sujet | Valeur provisoire | Où |
|---|---|---|---|
| H18 | Rayon de contrôle autour de Cayenne | 20 km autour du centre de Cayenne. Ce n'est pas la règle de la zone (ce sont les communes) : il rattrape seulement une position impossible, comme Kourou saisi avec « Cayenne ». Les « 5 km » de la visio couperaient une partie de Matoury (l'aéroport est à plus de 10 km) | `PILOT_ZONE_RADIUS_KM`, `services/place_service.py` |
| H18 | Rayon des offres pour un chauffeur | 10 km autour de sa position | `OFFER_RADIUS_KM`, `services/ride_rules.py` |
| – | Demande hors zone | Refusée (`422`) avec un message qui dit que le service ne couvre que Cayenne, Rémire-Montjoly et Matoury | Validation des lieux |
| UC81 | Kourou | Hors pilote ; s'ajoutera comme une donnée de référence | `sql/schema-mvp.sql` (équipe BD) |

### Suites de l'audit de sécurité (02/11/2026)

| # | Sujet | Valeur provisoire | Où |
|---|---|---|---|
| F4 | Inscription par code SMS | Gardée (simulée en MVP ; coût des vrais SMS à la mise en service) | `auth_service.py` |
| F6 | Plafond de courses non terminées par usager | 1 immédiate + 3 programmées | `MAX_OPEN_IMMEDIATE_RIDES`, `MAX_OPEN_SCHEDULED_RIDES`, `services/ride_rules.py` |
| F10 | Motif du trajet visible du chauffeur sur une offre | Le comportement actuel est gardé jusqu'à la réponse ; le client doit dire si le chauffeur en a besoin (un trajet « santé » est une donnée sensible) | DTO des offres |

### Appareils, notifications, abonnement

| # | Sujet | Valeur provisoire | Où |
|---|---|---|---|
| Q13 | Application | PWA installable, Android et iPhone | Aucun code |
| – | « Android/iOS » ou « Android prioritaire » | Les deux, testés d'abord sur Android | Tests |
| Q14 | SMS | Simulés : écrits dans les logs, sans numéro ni contenu personnel | `sms_repository.py` |
| UC73 | Notifications hors SMS | Hors MVP | – |
| UC79 | Abonnement mensuel | Hors MVP tant que le client ne le demande pas explicitement | – |
| – | Nouvelle version du cahier des charges | On travaille sur la version 1 (06/07/2026) | – |

---

## 4. Ce que ces décisions changent

À faire dans le code, chacun dans sa propre branche :

- **Commission (Q8)** : ajouter la constante `PLATFORM_COMMISSION_RATE` marquée
  `CHANGER_SELON_DECISION`, et montrer au chauffeur son revenu net dans « Mes revenus » (UC28).
  Si le taux peut changer en cours de pilote, chaque course doit garder le montant reversé au
  chauffeur au moment de sa clôture : c'est une colonne en plus sur `course`, **à demander à
  l'équipe BD** (H9), sans l'appliquer ici.
- **Marquage** : ajouter le commentaire `CHANGER_SELON_DECISION` sur les constantes déjà en place
  citées en partie 3 (tarif, plafonds, rayons, délais).
- **Photo du chauffeur** : l'afficher sur la page du trajet avec le prénom et la note (étape 4).
- **Opérateur (étape 6)** : UC40 à UC43 et UC45 sont maintenant tous dans le MVP ; UC44 reste
  dehors.

À mettre à jour dans la documentation :

- [cas-d-utilisation.md](cas-d-utilisation.md) : statut de UC41, UC45, UC56 ; mini CV dans UC15.
- [contrat-api.md](contrat-api.md) : H9, H14, H19 décidées ; commission dans les revenus.
- [CLAUDE.md](../CLAUDE.md), « Points à confirmer » : retirer ce qui est décidé ici.
