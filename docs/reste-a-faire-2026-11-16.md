# Ce qui reste à faire (état au 16/11/2026)

Le code s'arrête vers le **30/11** ; ensuite, tout le temps va à la présentation. On ne finit donc pas tout le palier P1 : on fait ce qui sert la démo du scénario A et ce que la SAÉ note, et on présente le reste comme une limitation.

Les tables de l'équipe BD sont livrées (migrations 009 à 027, PR #85 et #86) : ce qui manque, c'est l'API et les écrans.

## 1. Indispensable avant le 30/11

| # | Quoi | Pourquoi | Version minimale | Tables |
|---|---|---|---|---|
| 1 | ~~**Questionnaire et plan d'action (M1)**~~ (fait le 21/11, avec « Être rappelé ») | Début du scénario A, et seul morceau du fil rouge qui n'existe pas : sans lui, la démo commence au milieu | 5 ou 6 questions à choix, règles simples, plan de 3 étapes (une offre, un service d'aide, un trajet). Pas d'écran de reprise : la colonne existe en base, on le dit à l'oral | 017 |
| 2 | **Trajets dans MySQL** | Un redémarrage de l'API efface aujourd'hui tous les trajets : risqué en démo. La base est notée dans le rendu : l'API doit se servir du travail de l'équipe BD | Lire et écrire `course` et `evaluation` avec les colonnes existantes, sans les nouveaux états | `course`, `evaluation` |
| 3 | **Offres, services d'aide et fiches dans MySQL** | Rapide (tables et données prêtes, mêmes identifiants), et complète la preuve que tout passe par la base | Remplacer les trois repository en mémoire | 011 à 016 |
| 4 | **Statut du trajet en direct** | « Suivi en temps réel » cité par la SAÉ ; deux écrans côte à côte (usager, chauffeur) qui se mettent à jour seuls | Un événement `ride:updated` qui recharge la page du trajet ; `ride:offer` côté chauffeur si le temps le permet | – |
| 5 | **Répétition du scénario A** | La démo doit passer de bout en bout, sans surprise | Parcours de Jordan avec les comptes de `demo-data.sql` | – |

**Répartition proposée** : n° 1 et 4 pour un développeur, n° 2 et 3 pour l'autre. Rien d'autre avant que le scénario A passe de bout en bout.

## 2. Si le temps le permet, sinon présenté comme limitation

| Quoi | Effort | Ce qu'on dit à l'oral s'il n'est pas fait | Tables |
|---|---|---|---|
| ~~« Être rappelé »~~ (fait le 21/11) | Petit | Prévu et utile au public visé, table prête | `demande_aide` (027) |
| « Chauffeur arrivé » | Petit | État prêt en base, bouton non fait | `course` (020) |
| Réglages de l'administrateur : zones, horaires, tarifs | Moyen | Réglables en base, écran non fait ; valeurs provisoires en attente de la cliente | 010, 018, `tarif` |
| Passager absent, incident, paiement échoué, journal des étapes | Moyen | Schéma prêt (migrations 020 et 023), pas d'écran | 020, 023 |
| Pièces du chauffeur et suspension | Moyen | Schéma et vue prêts ; pièces vérifiées en personne pour l'instant | 024, 026 |
| Suppression de compte, signalement | Moyen | Schéma prêt, anonymisation décidée et imposée par la base | 002, 025, 027 |
| Repère, passagers, bagages | Moyen | Colonnes prêtes, pas dans le formulaire | 019 |
| Point sur une carte (Leaflet) | Abandonné | L'adresse suffit ; une dépendance de moins sur un réseau faible | – |
| Accessibilité de base | Petit (vérification) | Contrastes et clavier pris en compte dans la charte, sans audit complet | – |

## 3. Limitations à présenter

**Choix de périmètre (cahier des charges §5)**

| Limitation | Explication |
|---|---|
| Pas de suivi GPS en temps réel | Hors périmètre : seul le statut du trajet est en direct |
| Paiement simulé | L'usager ne paie rien dans le démonstrateur ; l'abonnement mensuel n'est pas codé |
| SMS simulés | Codes d'activation et de récupération écrits dans les logs |
| Données fictives, démo en local | Offres, services et comptes inventés ; pas d'hébergement (démonstrateur) |

**Limites techniques**

| Limitation | Explication |
|---|---|
| Géolocalisation du chauffeur | Peu fiable en arrière-plan dans une PWA : il faudrait une application native |
| État en mémoire | Inscriptions en attente, limites d'essais et verrous valables pour un seul processus d'API |
| Adresses et distances | OpenRouteService testé seulement avec de fausses réponses ; quotas non vérifiés ; ADR 020 (Géoplateforme de l'IGN) en suspens |
| Réseau faible | Objectif « Regular 2G » : chargement optimiste, allers-retours comptés. À présenter comme un choix d'architecture |

**Problèmes rencontrés (gestion de projet)**

| Problème | Ce qu'on en a fait |
|---|---|
| Cahier des charges reçu le 03/11, en milieu de projet, qui élargit le sujet du VTC à une « plateforme 360° » | Périmètre recalé sur le palier P1 et tracé dans `decisions.md` |
| Entretien du 03/11 qui contredit le cahier des charges (premier chauffeur disponible, gratuité, 5 langues) | Arbitrage écrit : l'entretien prime sur les points qu'il couvre |
| Coordination entre développeurs, équipe BD et cliente en Guyane | Issues `bd`, migrations numérotées, règle sur qui touche `sql/`, revue chaque mardi |
| Valeurs qui attendent la cliente (horaires, zones, tarifs, rémunération des chauffeurs) | Valeurs provisoires marquées `CHANGER_SELON_DECISION` |
| Traductions en créole non relues par des locuteurs | Texte français affiché quand une traduction manque |

## 4. En parallèle (hors code)

| Sujet | À faire |
|---|---|
| Maquettes | Validation par la cliente (revue du 17/11) |
| Dette front | Seulement #62 (brouillon de réservation sur un téléphone partagé) si le temps le permet ; le reste de #63 à #74 après la soutenance |
| Dossier conformité | Registre des traitements, matrice des flux, inventaire des dépendances : pour la transmission à la cliente (10/01) |

## 5. Après la soutenance (P2)

| Sujet | À faire |
|---|---|
| Bons solidaires | Tout (#25, en attente de la cliente) |
| Réservation pour autrui | Écrans du rôle `operator`, accord de la personne tracé et révocable |
| Notifications simulées | SMS dans un journal, notifications web, courriel de test |
| « Pourquoi cette proposition ? » | Explication sur chaque étape du plan d'action |
