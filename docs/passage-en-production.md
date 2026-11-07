# Passer du démonstrateur à une vraie application

Document de transmission, pour la personne ou l'équipe qui reprend « En route pour l'emploi »
après le projet étudiant (fin vers le 10/01/2027). Il dit **ce qui est réel et ce qui ne l'est
pas** dans l'application, **quelles options** existent pour en faire un vrai service, et **dans
quel ordre** s'y prendre.

Rédigé en novembre 2026 par l'équipe de développement. À relire avec la cliente (Ingeco
Territoires) avant la remise.

> **En une phrase** : le code est une bonne base (architecture en couches, tests, sécurité
> auditée, réseau faible pris en compte), mais **il ne peut pas être mis en ligne tel quel**.
> Il faut au minimum brancher la vraie base de données, l'héberger proprement, envoyer de vrais
> SMS, retirer les données de démonstration et régler les questions juridiques (données
> personnelles, transport de personnes).

## Sommaire

1. [Ce que contient le démonstrateur](#1-ce-que-contient-le-démonstrateur)
2. [Les décisions à prendre d'abord](#2-les-décisions-à-prendre-dabord)
3. [Trois chemins possibles](#3-trois-chemins-possibles)
4. [Les chantiers techniques](#4-les-chantiers-techniques)
5. [Les chantiers hors code](#5-les-chantiers-hors-code)
6. [L'ordre conseillé](#6-lordre-conseillé)
7. [Où regarder dans le code](#7-où-regarder-dans-le-code)

---

## 1. Ce que contient le démonstrateur

| Partie | État aujourd'hui | Pour un vrai service |
|---|---|---|
| Comptes, connexion, rôles | **Réel** : mots de passe hachés, sessions sécurisées, droits vérifiés côté serveur | À garder |
| Réservation, suivi, annulation, évaluation, côté chauffeur | **Réel** dans la logique, testé (~240 tests) | À garder |
| Données (comptes, trajets) | **En mémoire** : tout revient à zéro quand l'API redémarre. La base MySQL existe (schéma de l'équipe BD) mais l'API ne s'en sert pas encore pour les données métier | **À brancher** (chantier 4.1) |
| Comptes de test | Mot de passe public (`Trajet-2026!`), dont un administrateur | **À supprimer** (4.3) |
| SMS (codes, alertes) | **Simulés** : une ligne dans les journaux, rien n'est envoyé. Codes fixes en démo (`123456`, `12345678`) | **À brancher** sur un vrai prestataire (4.4) |
| Paiement | **Simulé** : un bouton « payer » sans carte | Selon le modèle choisi (2 et 4.5) |
| Adresses et distances | OpenRouteService si une clé est fournie, sinon une douzaine de lieux fictifs | Clé au nom de la structure, quotas à vérifier (4.6) |
| Temps réel | Absent : boutons « Actualiser » | Prévu (Socket.IO), à finir et sécuriser (4.7) |
| Langues | Français, anglais, portugais du Brésil complets ; deux créoles **vides** (s'affichent en français) | Faire écrire et relire les créoles (5.5) |
| Installation | Une commande (`docker compose up`), **en mode démo uniquement** | Configuration de production à écrire (4.2) |
| Hébergement | Aucun : la démo tourne sur un ordinateur | À choisir (4.2) |

Ce qui est provisoire (tarifs, délais, zones, règles d'annulation) est listé dans
[decisions.md](decisions.md) et repérable dans le code par `CHANGER_SELON_DECISION`.

---

## 2. Les décisions à prendre d'abord

Ces questions ne sont pas techniques, mais elles changent le travail à faire. Les trancher
**avant** de recruter ou de développer.

1. **Qui paie quoi ?** La cliente a évoqué un abonnement mensuel (~60 €), gratuit pour les
   personnes envoyées par une structure affiliée. Trois cas très différents :
   - **gratuit pour l'usager**, la structure paie les chauffeurs : pas de paiement en ligne du
     tout, le plus simple ;
   - **abonnement** : paiement récurrent, gestion des droits, factures ;
   - **prix par course** (ce que fait le démonstrateur) : paiement à chaque trajet,
     remboursements.
2. **Qui sont les chauffeurs ?** Salariés, bénévoles indemnisés, indépendants (VTC) payés à la
   course ? Cela décide du cadre légal (5.2), de la page « Mes revenus » et de la commission.
3. **Quelle échelle ?** Un pilote dans une seule structure (quelques dizaines d'usagers) ou un
   service ouvert à tout le territoire ?
4. **Qui maintient l'application ?** Une autre promotion d'étudiants, un prestataire, un
   développeur salarié ou bénévole ? Il faut **quelqu'un de responsable** des mises à jour de
   sécurité, même quand rien ne change.
5. **Quel budget par mois ?** Hébergement, SMS, nom de domaine, éventuellement paiement et
   maintenance.

---

## 3. Trois chemins possibles

### Chemin A : un pilote encadré (recommandé pour commencer)

Un service réel mais limité : une seule structure, des usagers inscrits par elle, quelques
chauffeurs connus, pas de paiement en ligne (trajets pris en charge par la structure).

- **À faire** : chantiers 4.1 à 4.4, 4.8 à 4.10, et 5.1 à 5.4.
- **On peut laisser de côté** : le paiement (4.5), le temps réel (4.7, les boutons
  « Actualiser » suffisent), les créoles si le public parle français.
- **Avantages** : le plus court ; on apprend des vrais usagers avant d'investir.
- **Limites** : ne passe pas à l'échelle sans les chantiers suivants.

### Chemin B : un service ouvert sur le territoire

Tout le chemin A, plus : paiement ou abonnement, temps réel, plusieurs structures et financeurs
(les « bons solidaires » du palier P2 du cahier des charges), centre d'appel, application plus
robuste.

- **À faire** : tous les chantiers des parties 4 et 5.
- **Avantages** : le service complet imaginé dans le cahier des charges.
- **Limites** : demande une équipe stable (au moins un développeur sur la durée), un budget
  récurrent et un accompagnement juridique.

### Chemin C : ne pas développer davantage

Garder le démonstrateur comme **maquette fonctionnelle** : il sert à montrer le besoin à des
financeurs, à rédiger un cahier des charges pour un prestataire, ou à comparer avec des
solutions de transport solidaire ou de transport à la demande qui existent déjà.

- **À faire** : rien de technique ; garder le dépôt et la documentation accessibles.
- **Avantages** : aucun coût de maintenance ; le travail des étudiants reste utile.
- **Limites** : le code vieillit (dépendances non mises à jour) : le relancer dans un an ou
  deux demandera un peu de remise à niveau.

---

## 4. Les chantiers techniques

Chaque chantier dit **quoi**, **pourquoi** et **les options**. L'effort est donné en ordre de
grandeur pour une personne qui découvre le code : petit (quelques jours), moyen (une à deux
semaines), gros (plus).

### 4.1 Brancher la vraie base de données — gros, obligatoire

Les données passent aujourd'hui par des listes en mémoire dans `BACKEND/app/repository/`.
L'architecture a été pensée pour ça : **seuls les fichiers de `repository/` changent**, les
services et les écrans restent les mêmes.

- Écrire les modèles SQLAlchemy dans `app/models/` d'après `sql/schema-mvp.sql` et
  `sql/migrations/`.
- Réécrire chaque `*_repository.py` en requêtes SQLAlchemy.
- Remplacer les verrous en mémoire par `SELECT … FOR UPDATE` (fiche
  [ADR 007](adr/007-etat-en-memoire.md)).
- Ajouter les tables qui manquent pour les modules du palier P1 non encore codés (offres,
  annuaire, questionnaire), en passant par des **migrations** numérotées.
- Base en production : **MySQL 8.4** (choix de l'équipe BD, [ADR 008](adr/008-mysql.md)). Un
  utilisateur MySQL **sans droit de modifier le schéma** pour l'API.

### 4.2 Héberger l'application — moyen, obligatoire

Il faut trois choses en ligne : la base, l'API (Python) et l'interface (fichiers statiques).

| Option | Pour qui | Points d'attention |
|---|---|---|
| **Plateforme gérée** (PaaS : on dépose le code, l'hébergeur fait tourner) | Équipe sans administrateur système | Plus cher à volume égal ; vérifier que les données restent dans l'Union européenne |
| **Serveur virtuel** (VPS) avec Docker Compose | Quelqu'un à l'aise avec Linux | Le moins cher ; mises à jour du serveur, pare-feu et sauvegardes à sa charge |
| **Hébergement de la collectivité ou d'un partenaire** | Si une structure publique peut héberger | Souvent gratuit ; délais et règles internes |

Dans tous les cas :

- **Hébergeur dans l'Union européenne**, de préférence en France (données personnelles d'un
  public fragile, et le motif « santé » d'un trajet est une donnée sensible : voir 5.1).
- **HTTPS obligatoire** et un nom de domaine au nom de la structure.
- Remplacer le serveur de développement : aujourd'hui `python -m app` lance le serveur de test de
  Flask. En production, un vrai serveur compatible avec Flask-SocketIO (par exemple Gunicorn avec
  un worker adapté) derrière un proxy (nginx ou celui de l'hébergeur), avec
  `TRUSTED_PROXY_COUNT` réglé.
- **Un seul processus d'API** tant que les limites d'essais et les inscriptions en attente sont
  en mémoire ([ADR 007](adr/007-etat-en-memoire.md)) ; pour plusieurs processus, ajouter Redis.
- Écrire une configuration de production à part : `compose.yaml` est **réservé à la démo**
  (comptes de test, cookies sans HTTPS).
- Coûts : de l'ordre de quelques dizaines d'euros par mois pour un pilote, à vérifier selon
  l'hébergeur au moment du choix.

### 4.3 Retirer tout ce qui est « démo » — petit, obligatoire

- `LOAD_DEMO_DATA=false` (l'API refuse déjà de démarrer avec les comptes de test quand les
  cookies sont en HTTPS).
- Ne jamais charger `sql/demo-data.sql` en production.
- Vérifier que les codes SMS fixes (`123456`, `12345678`) ne sont plus utilisés : ils ne le sont
  qu'avec les données de démo (`services/auth_service.py`).
- `API_DOCS_ENABLED=false`, `FLASK_DEBUG=false`, `COOKIE_SECURE=true`, une nouvelle
  `FLASK_SECRET_KEY` générée pour la production.
- Retirer ou adapter la mention « Projet étudiant — démonstrateur » et les textes « rien n'est
  réel » (page À propos, FAQ) **seulement quand** le service est réellement ouvert.

### 4.4 Envoyer de vrais SMS — petit à moyen, obligatoire

Les SMS servent à l'inscription, au mot de passe oublié et aux alertes de trajet. Tout passe par
**un seul fichier** : `BACKEND/app/repository/sms_repository.py`.

- Options : un prestataire d'envoi de SMS avec une API (plusieurs opérateurs et hébergeurs
  français en proposent). Vérifier la **couverture et le prix vers la Guyane** (numéros
  `0694`), ce n'est pas toujours le tarif de la métropole.
- Compte ouvert **au nom de la structure**, jamais d'un étudiant (README, « Comptes des
  services externes »).
- Garder la règle actuelle : aucun numéro ni contenu de SMS dans les journaux.

### 4.5 Le paiement — de rien à gros, selon la décision 2.1

- **Service gratuit pour l'usager** : retirer l'étape de paiement simulé et afficher « pris en
  charge ». Petit.
- **Prix par course** : brancher un prestataire de paiement en ligne (mode test d'abord), gérer
  le paiement échoué et les remboursements. Moyen à gros. Ne jamais stocker de numéro de carte :
  c'est le prestataire qui s'en charge.
- **Abonnement** : paiement récurrent, droits liés à l'abonnement, structures « affiliées »
  exonérées. Gros, et à concevoir avec la cliente.

### 4.6 Adresses et distances — petit

OpenRouteService (données OpenStreetMap) : une clé gratuite au nom de la structure. Vérifier les
**quotas gratuits** par rapport au nombre de recherches prévu et l'obligation de citer la
source ([ADR 009](adr/009-openrouteservice.md)). Si les quotas ne suffisent pas : offre payante,
ou installer son propre serveur OpenRouteService (gratuit mais demande un serveur costaud).

### 4.7 Le temps réel — moyen, utile surtout au chemin B

Prévu avec Socket.IO ([ADR 014](adr/014-socket-io.md)) : l'écran du trajet se met à jour seul.
**Avant de l'activer**, vérifier l'identité à la connexion (point F20 de
l'[audit de sécurité](audit-securite-2026-11-02.md)).

### 4.8 Sécurité — moyen, obligatoire

L'[audit du 02/11/2026](audit-securite-2026-11-02.md) a été corrigé pour l'essentiel. Restent à
faire avant une mise en ligne :

- **F3** : pouvoir couper toutes les sessions d'un compte (la colonne `version_session` existe en
  base, migration 001 : la brancher).
- **F15** : verrous en base au lieu des verrous en mémoire (avec 4.1).
- **F20** : politique de sécurité du contenu (CSP) pour l'interface, Socket.IO authentifié,
  échappement des recherches `LIKE`.
- Un nouvel audit, par quelqu'un d'extérieur, avant l'ouverture au public.

### 4.9 Sauvegardes et supervision — petit, obligatoire

- **Sauvegarde automatique** de la base chaque jour, gardée ailleurs que sur le serveur, et
  **une restauration testée** au moins une fois.
- Être prévenu quand l'API ne répond plus (la route `GET /health` est faite pour ça) et lire les
  erreurs (les journaux sont déjà structurés, au format JSON).

### 4.10 Mises à jour — petit, mais tout le temps

- Les versions des dépendances sont figées (`BACKEND/requirements.txt`,
  `FRONTEND/package-lock.json`). La CI GitHub signale les failles connues : **quelqu'un doit lire
  ces alertes et faire les mises à jour**, au moins une fois par mois.
- Mettre à jour le système du serveur si on choisit un VPS.

### 4.11 Pour plus tard

- **Application native pour les chauffeurs** : une application web (PWA) ne peut pas suivre la
  position du téléphone en arrière-plan de façon fiable. Si ce besoin devient important, il
  faudra une application Android/iOS pour les chauffeurs.
- **Modules du palier P2** : bons solidaires, réservation pour le compte d'une personne
  (prescripteur, centre d'appel). Décrits dans le cahier des charges et
  [cas-d-utilisation.md](cas-d-utilisation.md).

---

## 5. Les chantiers hors code

Ces points ne relèvent pas des développeurs, mais **bloquent une mise en service**. Les faire
valider par des personnes compétentes (juriste, délégué à la protection des données).

### 5.1 Données personnelles (RGPD)

- **Registre des traitements** et **mentions d'information** pour les usagers et les
  chauffeurs.
- **Analyse d'impact (AIPD)** très probablement nécessaire : public vulnérable, position des
  chauffeurs, et le motif « santé » d'un trajet révèle une information sensible. À confirmer
  avec un délégué à la protection des données.
- **Durées de conservation** des comptes, trajets et journaux, et la suppression de compte
  (décidée le 03/11/2026, voir [decisions.md](decisions.md)).
- Contrat de sous-traitance avec l'hébergeur et le prestataire de SMS.

### 5.2 Le cadre légal du transport

Transporter des personnes contre paiement est réglementé (VTC, taxi, transport d'utilité
sociale, bénévolat indemnisé…). Le bon cadre dépend de la réponse à la question 2.2. **À faire
valider par un juriste avant la première course réelle**, avec les **assurances** des chauffeurs
et de la structure.

### 5.3 Les documents pour les utilisateurs

Mentions légales, conditions d'utilisation, politique de confidentialité, et les règles
d'annulation et d'absence fixées par la structure (aujourd'hui des valeurs provisoires).

### 5.4 Les personnes autour de l'application

- **Un support** : qui répond quand un usager est bloqué ? Le cahier des charges prévoit un
  centre d'appel et un bouton « Être rappelé ».
- **Les chauffeurs** : recrutement, vérification des pièces (le compte n'est créé qu'après une
  vérification en personne), suivi de l'expiration des documents.
- **L'administrateur** : une personne de la structure formée à l'écran d'administration.

### 5.5 Langues et accessibilité

- Faire **écrire et relire** les textes en créole guyanais et haïtien par des locuteurs
  (fichiers `FRONTEND/src/i18n/gcr.ts` et `ht.ts`), et relire l'anglais et le portugais.
- Un audit d'accessibilité (référentiel RGAA) si l'application est portée par une structure
  publique ou financée par elle.

### 5.6 Comptes et propriété

- Transférer le dépôt GitHub et tous les comptes de services à la structure (README,
  « Remettre les accès en fin de projet »).
- Choisir la **licence** du code (MIT par défaut aujourd'hui, ou EUPL, ou cession à Ingeco) :
  question posée à la cliente.

---

## 6. L'ordre conseillé

Pour le chemin A (pilote encadré) :

1. **Décider** : modèle de paiement, statut des chauffeurs, qui maintient, budget (partie 2).
2. **Juridique en parallèle** : cadre du transport, assurances, RGPD (partie 5). C'est souvent
   le plus long : le lancer dès le début.
3. **Brancher la base** (4.1), puis **retirer la démo** (4.3).
4. **SMS réels** (4.4) et **paiement** selon la décision (4.5).
5. **Sécurité** restante (4.8).
6. **Hébergement** de test, avec HTTPS, sauvegardes et supervision (4.2, 4.9).
7. **Tester avec quelques vrais usagers et chauffeurs** de la structure, sur une période courte.
8. **Ouvrir le pilote**, avec une personne chargée des mises à jour (4.10).

---

## 7. Où regarder dans le code

| Pour… | Lire d'abord |
|---|---|
| Comprendre l'organisation | [README.md](../README.md), [architecture.md](architecture.md), [CLAUDE.md](../CLAUDE.md) |
| Savoir pourquoi un choix a été fait | [docs/adr/](adr/README.md) |
| Les valeurs provisoires à changer | [decisions.md](decisions.md), et `CHANGER_SELON_DECISION` dans le code |
| Brancher la base | `BACKEND/app/repository/`, `BACKEND/app/models/`, `sql/` |
| Les SMS | `BACKEND/app/repository/sms_repository.py` |
| Le paiement simulé | `BACKEND/app/services/ride_service.py` (`pay_ride`) |
| La configuration | `BACKEND/app/config.py`, `BACKEND/.env.example`, `compose.yaml` |
| La sécurité | [audit-securite-2026-11-02.md](audit-securite-2026-11-02.md) |
| Les textes et langues | `FRONTEND/src/i18n/` |
| Ce que veut la cliente | [cahier des charges](cahier-des-charges-v1.0.docx), [entretien du 03/11](compte-rendu-entretien-2026-11-03.md) |
