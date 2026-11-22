# Ce qui reste à faire (état au 22/11/2026)

Remplace [reste-a-faire-2026-11-16.md](reste-a-faire-2026-11-16.md). Fait à partir d'une
comparaison ligne à ligne du [cahier des charges v1.0](cahier-des-charges-v1.0.docx) (palier P1,
critères d'acceptation §18, conformité §13, livrables §17) avec le code de `main`, en tenant compte
de l'[entretien du 03/11](compte-rendu-entretien-2026-11-03.md) et de [decisions.md](decisions.md).

**Calendrier** : arrêt du code vers le **30/11** (8 jours), gel le **10/12**, soutenance le **14 ou
15/12**, transmission à la cliente vers le **10/01/2027**.

## Sommaire

- [0. Fait depuis le 16/11](#0-fait-depuis-le-1611)
- [1. Code : le P1 qui manque](#1-code--le-p1-qui-manque)
- [2. Conformité et RGPD](#2-conformité-et-rgpd)
- [3. Livrables hors code](#3-livrables-hors-code)
- [4. Questions à la cliente](#4-questions-à-la-cliente)
- [5. Dette front (issues #62 à #74)](#5-dette-front-issues-62-à-74)
- [6. Après la soutenance (P2)](#6-après-la-soutenance-p2)
- [7. Limitations à présenter](#7-limitations-à-présenter)
- [8. Ce qu'on a fait en plus du P1](#8-ce-quon-a-fait-en-plus-du-p1)

## 0. Fait depuis le 16/11

Toute la partie « Indispensable » du 16/11 est faite :

| Quoi | État |
|---|---|
| Questionnaire d'orientation et plan d'action (M1), avec « Être rappelé » | Fait le 21/11 |
| Trajets et évaluations dans MySQL (avec le journal `etape_course`) | Fait |
| Offres, services d'aide et fiches pratiques dans MySQL (#48, #49) | Fait |
| Statut du trajet et offres des chauffeurs en direct (Socket.IO, PR #96) | Fait le 21/11 |
| Répétition du scénario A (Jordan) | Faite en parallèle (22/11) |

## 1. Code : le P1 qui manque

Classé par priorité. **A** : à faire avant le 30/11, parce qu'un critère d'acceptation P1 ou le jury
le demande. **B** : si le temps le permet. **C** : présenté comme limitation, sans code.

| Prio | Quoi | Exigence | Tables | Version minimale | Effort |
|---|---|---|---|---|---|
| **A** | **Refus d'une demande hors horaire, avec une explication** | §18 P1 : « Une demande hors zone ou hors horaire est bloquée avec une explication ». La zone est faite, l'horaire non | `horaire_service` (018) | Lire les plages dans `ride_service` à la création et à l'estimation, refuser en `422` avec un message simple (« Le service fonctionne de 6 h à 20 h ») ; calcul dans le fuseau `America/Cayenne` ; tests sur les dates | Petit |
| **A** | **Masquer le motif dans les offres des chauffeurs** | §7.4, §12, RGPD art. 9 : voir partie 2 | – | `OfferDto` sans `purpose` (ou motif seulement après acceptation) ; régénérer les types | Petit |
| **A** | **Réglages de l'administrateur : horaires, zones, tarifs** | §5 M9 P1, US07 | 010, 018, `tarif` | Un écran par réglage, liste + modification ; nouvelle version du tarif plutôt que modification (la version acceptée est conservée, §7.4) | Moyen |
| B | **« Chauffeur arrivé »** | §7.4 P1 (états) | `course` (020), `etape_course` (023) | Route `POST /rides/{id}/arrive`, bouton côté chauffeur, étape horodatée avec auteur, `ride:updated` | Petit |
| B | **« Passager absent »** et **incident** | §7.4 P1 (étapes horodatées avec auteur) | 020, 023 | Deux routes chauffeur, deux boutons, étapes au journal | Petit |
| B | **Demande de suppression de compte** | §6 P1 | `demande_suppression` (002), 025 | Bouton dans le profil, traitement par l'administrateur (anonymisation décidée : `decisions.md`) | Moyen |
| B | **« Signaler un problème »** | §6 (aide) | `demande_aide` (027, type `signalement`) | Même modèle qu'« Être rappelé » : un texte court, enregistré | Petit |
| B | **Repère et nombre de passagers** dans le formulaire de réservation | §3, §7.4 P1 | 019 | Un champ texte « Repère » et un choix 1 à 4 sur l'écran d'horaire | Petit |
| B | **Accessibilité de base** : vérification | §6, §11 P1 | – | Passage clavier sur les parcours du scénario A, contrastes vérifiés, libellés ; noter le résultat | Petit |
| C | Bagages | §7.4 | – | Limitation | – |
| C | Point sur une carte | §3, §7.4 | – | Abandonné : l'adresse et le repère suffisent, une dépendance lourde de moins en 2G | – |
| C | Dossier chauffeur complet (places, zones, disponibilités, pièces) et suspension à l'expiration | §7.4 P1 | 024, 026 | Limitation : pièces vérifiées en personne par l'administrateur, schéma et vue prêts | – |
| C | Paiement échoué | §7.4 | 020 | Limitation : l'usager ne paie rien dans le démonstrateur | – |
| C | Reprise du plan d'action par un conseiller | M1 | 017 | Colonnes prêtes, pas d'écran | – |

**Retirés exprès, à ne pas faire** (entretien du 03/11) : affectation et réaffectation par
l'administrateur, délai de réponse et refus d'une proposition par le chauffeur (US06, US07). Le
premier chauffeur disponible prend la course.

## 2. Conformité et RGPD

Aucune pratique interdite par le cahier des charges n'a été trouvée : pas de champ interdit (§12),
pas de décision automatique ni d'IA de tri (§13.1), pas de service d'urgence promis (§6), SMS
simulés sans numéro ni texte dans les logs, paiement simulé, nom d'Ingeco non utilisé sans accord.
Trois zones grises restent à traiter ou à argumenter :

| Point | Risque | Ce qu'on fait |
|---|---|---|
| **Motif « santé » visible de tous les chauffeurs** dans les offres, avant acceptation | « Trajet santé » + adresse d'arrivée renseigne sur la santé (donnée sensible, RGPD art. 9). La liste de motifs du cahier des charges (§7.4) ne comprend pas la santé | Masquer le motif dans les offres (partie 1, priorité A) ; question à la cliente : le chauffeur en a-t-il besoin ? |
| **Position du chauffeur envoyée toutes les 30 s** tant qu'il est disponible | Le suivi GPS en temps réel est hors périmètre (§5) | Défendable : jamais montrée au passager, seule la dernière position est gardée, effacée hors ligne, jamais dans les logs. À l'oral : « sa dernière position sert à lui proposer les courses proches », pas « on suit le chauffeur » |
| **Abonnement mensuel (~60 €) prévu par la cliente** | §13.1 P1 : gratuité totale du service pour les demandeurs d'emploi (C. trav. L.5321-3) | Rien de codé, trajets gratuits dans le démonstrateur. À signaler par écrit à la cliente : le montage juridique est à sa charge (§13.2) |

## 3. Livrables hors code

| Quoi | Exigence | État | Pour quand |
|---|---|---|---|
| **Fichier `LICENSE`** | §14, §17 | **Absent** : le choix entre MIT, EUPL 1.2 et cession attend la cliente | Dès la réponse ; sinon le dire à l'oral |
| **Registre simplifié des traitements** | §13 P1 | Absent | Avant la soutenance (au moins un brouillon) |
| **Matrice des flux** (qui transmet quoi, à qui, pourquoi) | §12, §13 P1 | Absente. Doit citer OpenRouteService, qui reçoit les adresses saisies | Avant la soutenance |
| **Inventaire des dépendances et de leurs licences** | §14, §17 | Absent | Avant la transmission (10/01) |
| Maquettes de tous les parcours validées par la cliente | §10 | Partiel (`docs/maquettes/`) | Revue du mardi |
| Rapport de gestion (répartition, temps, réunions, démos), déclaration de l'usage de l'IA | SAÉ, §14 | À écrire | Soutenance |
| Support de soutenance, vidéo de 5 min du scénario A | §17 | À faire | Soutenance |
| Guide utilisateur en langage simple, guide administrateur | §17 | À faire | Transmission |
| Note de transmission (paliers atteints, backlog restant, dette, coûts) | §17 | Base : [passage-en-production.md](passage-en-production.md) | Transmission |
| Fiche de cadrage signée | §21 | Non signée | Avec la cliente |

## 4. Questions à la cliente

- Le chauffeur a-t-il besoin de connaître le **motif** du trajet ? (et avant ou après avoir accepté)
- **Horaires autorisés** du service (valeur provisoire dans `decisions.md` en attendant).
- **Licence** (MIT, EUPL 1.2 ou cession) et convention tripartite.
- **Abonnement** et gratuité pour les demandeurs d'emploi (§13.1) : à faire vérifier de son côté.
- Relecture des textes en créole guyanais et haïtien ; usage du nom et du logo d'Ingeco.

## 5. Dette front (issues #62 à #74)

Après la soutenance, sauf **#62** (effacer le brouillon de réservation à la déconnexion, téléphone
partagé) si le temps le permet. Aucune ne bloque le scénario A.

## 6. Après la soutenance (P2)

| Sujet | À faire |
|---|---|
| Bons solidaires (#25) | Tout, en attente de la cliente : tiers payeur, plafonds, enveloppes, un seul financeur par trajet |
| Réservation pour autrui | Écrans du rôle `operator`, accord de la personne tracé et révocable |
| Notifications simulées | SMS dans un journal, notifications web, courriel de test |
| « Pourquoi cette proposition ? » | Explication sur chaque étape du plan d'action |
| Règles d'annulation et d'absence réglables | §7.4, §18 P2 |

## 7. Limitations à présenter

| Limitation | Explication |
|---|---|
| Pas de suivi GPS en temps réel | Hors périmètre (§5) : seul le statut du trajet est en direct |
| Paiement et SMS simulés | L'usager ne paie rien ; codes d'activation et de récupération dans les logs |
| Données fictives, démo en local | Démonstrateur, pas un service en production (§1) |
| Point sur carte, bagages, dossier chauffeur complet, paiement échoué | Voir partie 1, priorité C ; schéma prêt en base pour la plupart |
| Géolocalisation du chauffeur | Peu fiable en arrière-plan dans une PWA : il faudrait une application native |
| État en mémoire | Inscriptions en attente et limites d'essais valables pour un seul processus d'API |
| OpenRouteService | Testé avec de fausses réponses ; quotas non vérifiés |
| Traductions en créole | Non relues par des locuteurs ; le français s'affiche quand une traduction manque |

## 8. Ce qu'on a fait en plus du P1

À valoriser à l'oral : ce n'est pas du hors-périmètre, c'est demandé par la SAÉ, par la cliente, ou
fait avant le cahier des charges et gardé par décision du 03/11.

- **Demandé par la SAÉ** : évaluation du trajet, statut en direct (Socket.IO).
- **Demandé par la cliente (03/11)** : 5 langues (le P1 n'en demande que la structure), accueil
  illustré, trajets gratuits, photo du chauffeur.
- **Codé avant le cahier des charges** : réservation immédiate (§20, évolution), paiement simulé et
  remboursement (P2), désistement du chauffeur et anti-doublon par verrous MySQL (P3), revenus du
  chauffeur, usager prioritaire, expiration automatique, courses proches du chauffeur.
- **Choix d'équipe** : objectif « Regular 2G » (plus exigeant que la 3G du §11), audio des fiches par
  la synthèse vocale, plan d'action gardé avec « C'est fait », OpenAPI et types générés, CI, limites
  d'essais et en-têtes de sécurité, ADR pour chaque choix technique.
