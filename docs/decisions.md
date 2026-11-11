# Décisions et valeurs provisoires

Ce document est **la référence pour la suite du développement** : il dit ce qui est décidé, et
quelle valeur provisoire on applique à tout ce qui ne l'est pas encore. Il complète
[points-a-valider-porteur.pdf](points-a-valider-porteur.pdf) (questions Q1 à Q15, propositions
A à F) et les hypothèses H1 à H19 de [contrat-api.md](contrat-api.md#7-hypothèses-et-questions-ouvertes).

- **Première version** : 03/11/2026, réponses transmises par Denis ZAPOI.
- **03/11/2026, plus tard** : le [cahier des charges v1.0](cahier-des-charges-v1.0.docx) devient la
  **source de vérité**. Ce qu'il fixe est dans la [partie 2](#ce-que-fixe-le-cahier-des-charges-v10)
  et remplace les réponses et valeurs provisoires contraires, corrigées dans la partie 3.
- **03/11/2026, entretien avec la cliente** : ses réponses, postérieures au cahier des charges,
  priment sur lui pour les points qu'elles couvrent (attribution des courses, langues, accueil,
  abonnement et gratuité) : [partie 2](#réponses-de-la-cliente-du-03112026-entretien) et
  [entretien du 03/11](compte-rendu-entretien-2026-11-03.md).
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

### Réponses de la cliente du 03/11/2026 (entretien)

Données après la réception du cahier des charges : **elles priment sur lui** pour ce qu'elles
couvrent. Détail et questions restantes : [entretien du 03/11](compte-rendu-entretien-2026-11-03.md).

| Sujet | Décision | Ce que ça remplace | Conséquence |
|---|---|---|---|
| Périmètre | Tout le socle, y compris l'emploi | – | Confirme tout le palier P1 |
| Attribution des courses | **Le premier chauffeur disponible prend la course**, depuis sa page qui liste les courses en attente autour de lui. L'administrateur n'affecte pas les courses | Cahier des charges : affectation et réaffectation par l'administrateur, proposition à un chauffeur avec délai de réponse et refus (§5 M4 et M9 P1, §7.4) | Déjà codé (offres proches, « Accepter », une course à un seul chauffeur). **Retirés du sprint 1** : affectation et réaffectation par l'administrateur, délai de réponse, refus d'une offre. Pas de décision automatique : c'est le chauffeur qui choisit (RGPD art. 22 respecté) |
| Langues | Français, **créole guyanais, créole haïtien, portugais du Brésil, anglais** | « Une langue de démonstration fournie par le porteur » (P2) | Sélecteur avec 5 langues (sprint 1, fait : [ADR 017](adr/017-cinq-langues.md) ; anglais et portugais complets, créoles vides et affichés en français). Rédaction et relecture des traductions : partie 3 |
| Accueil | Une **image** sur l'inclusion, le transport, le travail ; **plus de couleurs** ; un rendu plus abouti, en restant léger | Charte : « pas d'illustration décorative en image », deux couleurs | Refonte de l'accueil et de la [charte graphique](charte-graphique.md) (sprint 1), avec un poids d'image limité et testé en « Regular 2G » |
| Tarification | **Abonnement mensuel** (de l'ordre de 60 €) qui donne droit aux courses, **gratuit** pour une personne envoyée par une structure affiliée (France Travail, par exemple). Pour l'instant l'application ne sert que dans la structure de la porteuse : **entièrement gratuite** | Prix par course (§7.4) ; « abonnement hors projet » ; paiement simulé par course | Dans le démonstrateur, **l'usager ne paie rien**. Le paiement par course et la commission (Q8) sont en suspens ; affichage du prix, abonnement et rémunération des chauffeurs : partie 3 |

### Ce que fixe le cahier des charges v1.0

Le cahier des charges prime sur tout autre document (expression des besoins, réponses du
13/10/2026, première visio, contrat d'API, nos hypothèses). On ne pose à la cliente que ce qu'il
ne tranche pas, ce qu'il laisse à son choix, ou ce qui reste flou. Les § renvoient à ses parties.

| Sujet | Ce que fixe le cahier des charges | Ce que ça remplace | Conséquence |
|---|---|---|---|
| Statut d'Ingeco | Association loi 1901 (§1) | « SAS à mission » de l'expression des besoins | README, CLAUDE.md, rapport, page À propos |
| Nature du livrable | Un démonstrateur testé, documenté et transmis, pas un service en production (§1, §13.2) | « Le service démarre en janvier 2027 » | Fin de projet : note de transmission et remise des accès (README, « Comptes des services externes ») |
| Périmètre | Toutes les équipes livrent le palier P1 (§5) | Notre périmètre « MVP », centré sur le VTC | **Décision du 03/11 : tout le palier P1**, sur tous les modules qui en ont un. Le scénario A (§8, Jordan) est le fil rouge de la démonstration (CLAUDE.md, « Périmètre ») |
| Orientation (M1) | Questionnaire court et visuel (situation, projet, expériences y compris informelles, disponibilités, freins exprimés en besoins, langue, équipement), plan d'action en 3 à 5 étapes par des règles simples, avec services proposés et contact humain ; aucune décision automatique (§7.1, P1) | – | Sprint 2 (tables à demander à l'équipe BD). Contenu du questionnaire : partie 3 |
| Emploi (M2) | Jeu d'offres fictives ; filtres commune, horaires, débutant accepté, sans diplôme ; « Comment y aller ? » sur chaque offre ; un trajet se demande en 3 actions au plus depuis une offre, motif prérempli (§7.2, §18, P1) | – | Sprint 1 sur données factices, sprint 2 en base |
| Formation (M3) | Liens vers des catalogues existants (P1) | – | Sprint 1 : une page de liens |
| Annuaire (M5) | Services d'aide (garde, logement, droits, santé, aide alimentaire, numérique, démarches, équipement) avec langues parlées, horaires, accessibilité, date de mise à jour ; fiches pratiques « Comment faire ? » en langage simple ; données de démonstration (§7.5, P1) | – | Annuaire : sprint 1, fait sur données factices (`/aide/services`, 16 services, 2 par besoin), sprint 2 en base (issue #49). Fiches pratiques : sprint 1, PR suivante |
| Accueil | Organisé par besoins : « Je cherche un travail », « J'ai besoin d'un trajet », « J'ai besoin d'aide » ; 3 actions principales au plus (§10) | Accueil par fonctionnalités | Sprint 1, fait (illustration provisoire) |
| Maquettes | Maquettes de tous les parcours validées par le porteur avant développement (§10) | – | Maquettes des nouveaux parcours au début du sprint 1, montrées à la cliente |
| Suivi en temps réel | Le suivi GPS en temps réel est hors périmètre (§5) | Étape 4 : carte avec la position du chauffeur (`driver:location`) | **Décision interne du 03/11** : statut du trajet et offres mis à jour en direct, sans position du chauffeur montrée au passager. Présenté à la SAÉ comme son « suivi en temps réel ». La position du chauffeur sert toujours à lui proposer les courses proches |
| Attribution des courses | Affectation et réaffectation par l'administrateur, avec avertissement du passager ; propositions au chauffeur avec un délai de réponse, qu'il accepte ou refuse ; une course à un seul chauffeur (§5 M4 P1, §7.4, US06, US07) | « Le premier chauffeur qui accepte la prend », sans affectation | **Remplacé par l'entretien du 03/11** : le premier chauffeur disponible prend la course, pas d'affectation par l'administrateur |
| Horaires | Horaires autorisés réglables par l'administrateur ; une demande hors horaire est refusée avec une explication (§5 M9 P1, §18) | Proposition A et « 24h/24 » : aucune restriction | À ajouter (sprint 2, table à demander à l'équipe BD). Valeur provisoire en partie 3 |
| Zones | Zones desservies réglables, zones non desservies signalées (§3, §5 M9 P1) | Liste de communes figée | Écran administrateur (sprint 2). Valeur provisoire : les 3 communes du pilote |
| Tarifs | Réglés par l'administrateur (§5 M9 P1, US07) ; version du tarif acceptée conservée (§7.4) | – | Écran administrateur (sprint 2). Les montants restent provisoires (Q10) |
| Avant l'envoi | Prix total, réduction, reste à payer et conditions d'annulation affichés (§7.4) | – | Conditions d'annulation affichées à l'écran de confirmation (sprint 1, fait) : `CancellationTerms.tsx`, textes `booking.cancel*` |
| Demande de trajet | Départ et arrivée par adresse, **repère ou point sur carte** ; passagers, bagages, besoins de prise en charge (§3, §7.4) | Adresse choisie dans une liste seulement | Repère et nombre de passagers (colonnes, équipe BD) ; carte pour placer un point |
| États d'une course | Brouillon → demande envoyée → attente de chauffeur → confirmée → **chauffeur arrivé** → en cours → terminée ; refusée faute de disponibilité, annulée, **passager absent**. Paiement : en attente, payé, **échoué**, remboursé (§7.4) | Nos 7 états, sans « arrivé », « absent » ni paiement échoué | Nouvelles valeurs à demander à l'équipe BD. « Refusée faute de disponibilité » = notre expiration (UC60) |
| Étapes horodatées | Arrivée, début, fin, absence, incident : horodatés, avec leur auteur (§7.4) | Seul l'auteur d'une annulation est gardé | Colonnes ou table d'événements à demander à l'équipe BD |
| Annulation et absence | Paramètres : annulation gratuite, frais après échéance, absence du passager, annulation du chauffeur (§7.4) ; règles appliquées au palier P2 (§18) | Q7 : remboursement intégral comme règle fixe | Les règles deviennent des réglages ; valeurs provisoires en partie 3 |
| Dossier du chauffeur | Véhicule, places, zones, disponibilités, pièces ; activation après validation ; suspension à l'expiration des pièces (§7.4) | « Rien n'est stocké » sur les pièces | Pièces et dates d'expiration (équipe BD), suspension automatique avec reprise possible par l'administrateur |
| Compte | Inscription par téléphone avec code simulé, sans courriel obligatoire ; récupération d'accès ; **demande de suppression** (§6 P1) | Audit F4 (« inscription par SMS, à confirmer ») | F4 tranché. Demande de suppression à ajouter (sprint 2) : la table `demande_suppression` est livrée (migration 002), le sort du compte supprimé est décidé plus bas |
| Langues | Textes dans des fichiers de traduction, changement de langue à tout moment (§6 P1) ; une langue de démonstration fournie par le porteur (P2) | « Français seul, sans sélecteur » | Sélecteur de langue (sprint 1). **Langues données à l'entretien du 03/11** : français, créole guyanais, créole haïtien, portugais du Brésil, anglais |
| Aide | Bouton « Être rappelé », FAQ, signalement d'un problème ; aucun service d'urgence promis (§6) | – | Page « J'ai besoin d'aide » (`/aide`) et FAQ (`/aide/questions`) (sprint 1, faits ; textes `faq.*` à faire relire par la cliente), « Être rappelé » et signalement (sprint 2, stockage à demander) |
| Notifications | SMS simulés dans un journal, notifications web, courriel de test (§6 P2) | UC73 : notifications hors SMS hors MVP | Palier P2 : après la soutenance |
| Solidarité (bons) | Tarifs solidaires, plafonds, tiers payeur, codes de trajet (§5 M4 P2) ; éligibilité validée par un prescripteur avec motif, validité et plafond (§7.8) ; enveloppes par financeur, chaque trajet imputé à un seul financeur, réductions bloquées si l'enveloppe est épuisée (§7.9) | Q5, Q6 (forme du bon), C (« tarif unique »), Q9 (sans carte bancaire : bon à 100 %) | Le modèle des bons suit ce cadre (P2, après la soutenance) ; une personne sans carte passe par le tiers payeur ou un code de trajet. Restent les montants |
| Réservation pour autrui | Un prescripteur ou un accompagnant réserve pour une personne, avec son accord tracé et révocable (§6 P2, §7.8) ; rôle distinct d'« agent de réservation » (§7.9, P3) | Écran opérateur au sprint 2 | Après la soutenance. Le rôle `operator` correspond à l'agent de réservation |
| Base de données | Stack libre, justifiée par une fiche de décision ; PostgreSQL seulement recommandé (§11) | – | On reste sur MySQL ([ADR 008](adr/008-mysql.md)), confirmé par l'équipe BD le 03/11 (PR #36) |
| Appareils | PWA ; tests sur un Android d'entrée de gamme ou en émulation (§3, §20) | « Android/iOS ou Android prioritaire ? » | Tests d'abord sur Android d'entrée de gamme ; l'iPhone reste supporté par la PWA |
| Prix du trajet | Le trajet a un prix, réduit par les aides solidaires (§7.4, §7.9) ; la gratuité du code du travail (art. L.5321-3) vise le service d'accompagnement | Question 10 du 04/11 | **Remplacé par l'entretien du 03/11** : abonnement mensuel, gratuit dans la structure de la porteuse, donc trajets gratuits dans le démonstrateur |
| Hors périmètre | Données et paiements réels, envoi massif de SMS, mise en ligne publique, stores, suivi GPS en temps réel, décision automatisée, IA de tri (§5) | – | L'abonnement, absent du cahier des charges, **revient avec l'entretien du 03/11** (partie 2, « Tarification ») |
| Fonctions déjà codées hors du palier P1 | Le cahier des charges classe certaines fonctions en évolution future ou aux paliers P2 et P3 (§5, §20) | – | **Décision du 03/11** : ce qui est déjà codé reste tel quel, sans retravail : réservation immédiate (« évolution possible », §20), paiement simulé et annulation remboursée (P2), désistement du chauffeur et anti-doublon (P3), revenus du chauffeur, statut d'usager prioritaire. On ne retouche que ce que le cahier des charges contredit |

### Réponses du client et décisions internes

| # | Sujet | Décision | Conséquence |
|---|---|---|---|
| Q1, H14 | Paiement d'une réservation par téléphone | **Lien de paiement envoyé par SMS** (simulé en MVP). La carte dictée à l'opérateur est écartée : elle impose trop de contraintes de sécurité au centre d'appel | UC45 passe de « à trancher » à **MVP simulé** (étape 6). Contrat [6.9](contrat-api.md#69-lien-de-paiement-par-sms) confirmé |
| Q2 (en partie) | Droits de l'opérateur | L'opérateur **peut créer un compte à la place de l'usager**, en plus de réserver | UC41 confirmé (étape 6). Annuler et consulter les trajets passés : voir partie 3 |
| Q15 | Tableau de bord administrateur | **Libre** : le contenu est au choix de l'équipe | UC56 (étape 7) n'attend plus de réponse. Point de départ : l'hypothèse de Q15 (trajets par jour, par commune et par motif, trajets financés et montants, note moyenne) |
| Q10, H8 | Montants du tarif | **On garde le tarif provisoire** : 8 € de prise en charge + 0,80 €/km | Rien à changer : déjà dans `sql/schema-mvp.sql` et les données factices. Reste marqué `CHANGER_SELON_DECISION` tant que le client ne donne pas les montants définitifs |
| Q8, H9 | Commission de la plateforme | **En suspens depuis l'entretien du 03/11** : sans prix par course, elle n'a plus de sens tant qu'on ne sait pas comment les chauffeurs sont payés. Ne pas la coder | Revenus du chauffeur (UC28) : voir partie 3 |
| H19 | Profil du chauffeur montré au passager (« mini CV ») | **Prénom, note moyenne et photo**. Rien d'autre | Prénom et note déjà renvoyés par l'API (`firstName`, `averageScore`). La photo n'est servie qu'à l'administrateur : la route `GET /rides/{id}/driver-photo` pour le passager et l'affichage sur la page du trajet restent à faire (étape 4). Aucun champ de profil en plus en base |
| – | Rôle de l'équipe BD | **Tout le dossier `sql/` est à elle** : schéma, migrations, données de référence et de test, index. Les développeurs n'y touchent plus. **Migrations** : fichiers SQL numérotés (`sql/migrations/NNN_description.sql`), à partir du schéma v2 une fois validé. **Requêtes** : partagées, les courantes par les développeurs (SQLAlchemy, `repository/`), les lourdes par l'équipe BD en vues SQL (statistiques, chauffeurs proches, consommation des bons) | README, partie 5 ; CLAUDE.md ; architecture.md. Changement de schéma demandé par une issue GitHub avec l'étiquette `bd` |
| – | Compte supprimé (décision interne du 03/11, #32) | Statut **`supprime`** sur le compte : il ne se connecte plus et sort des listes. Nom et courriel effacés ; téléphone remplacé par **`+000` suivi de l'identifiant sur 9 chiffres** (`+000000000042`) : l'indicatif 000 n'existe pas, et la valeur respecte la contrainte du téléphone (unique, `+` et 8 à 15 chiffres). Les courses restent, sans identité | Migration demandée à l'équipe BD (#32) ; traitement de la demande par l'administrateur au sprint 2 |
| – | Démo de la soutenance (décision interne du 03/11, #26) | **En local**, sur un poste de l'équipe. Pas d'hébergement de la base à choisir : le livrable est un démonstrateur (cahier des charges §1) | L'équipe BD documente un export par `mysqldump` |
| – | Numéros de téléphone entre usager et chauffeur | **Oui, partagés pendant la course**, pour qu'ils puissent s'appeler à la prise en charge | Déjà fait : le numéro n'est renvoyé que pendant une course acceptée ou en cours. Différence avec Uber : Uber masque le vrai numéro derrière un numéro relais ; ici le vrai numéro est montré, seulement pendant la course |
| H18 | Zone du pilote | **Celle donnée en visio** ([compte-rendu-visio-1.md](compte-rendu-visio-1.md)) : Cayenne et environ 5 km autour, avec Rémire-Montjoly et Matoury (Cogneau-Lamirande). Départ et arrivée doivent être dans l'une de ces 3 communes | Déjà la règle de l'API (liste des communes). Ces 3 communes deviennent la valeur de départ des zones réglables par l'administrateur (cahier des charges, M9). Le rayon de contrôle reste provisoire : voir partie 3 |

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

### Bons solidaires (palier P2, après la soutenance)

Le cadre est fixé par le cahier des charges ([partie 2](#ce-que-fixe-le-cahier-des-charges-v10),
« Solidarité ») : éligibilité validée par un prescripteur (motif, validité, plafond), enveloppe
par financeur, un seul financeur par trajet, tiers payeur et codes de trajet. Les anciennes
valeurs provisoires sur la forme du bon (Q5, Q6) et l'usager sans carte (Q9) sont remplacées.

| # | Sujet | Valeur provisoire | Où |
|---|---|---|---|
| – | Montants : plafond par personne, taux de réduction, taille des enveloppes | À demander à la cliente quand on attaquera le P2 | Tables à demander à l'équipe BD à ce moment-là |
| Q12 | Ce que voit la structure qui finance | Date, communes et montant de chaque trajet ; ni nom, ni adresse, ni motif (cohérent avec les rapports agrégés et la pseudonymisation du cahier des charges) | `GET /partners/me/consumption` |
| H16 | Réduction rendue si la réservation expire ou est annulée | Oui, l'enveloppe est recalculée (§18) | Expiration (UC60), annulation (UC16) |

### Courses, paiement, annulation

| # | Sujet | Valeur provisoire | Où |
|---|---|---|---|
| A | Horaires autorisés (réglables, cahier des charges M9) | 0 h – 24 h, tous les jours, tant que la cliente n'a pas donné ses horaires : le mécanisme existe, la valeur ne bloque rien | Table des horaires à demander à l'équipe BD ; règle dans la réservation |
| B | Prix | Prise en charge + prix au km, annoncé avant paiement, figé ensuite (déjà en place) | `ride_rules.price_cents` |
| C, H8 | Tarif de base | Même tarif de base pour tous (palier P1) ; les réductions solidaires viennent avec le P2 | Table `tarif` |
| D, H16 | Aucun chauffeur trouvé | Recherche pendant 15 min, puis expiration, remboursement, nouvelle demande possible (déjà en place, UC60) | Constantes de l'expiration |
| H16 | Délai pour payer | 15 min, sinon la réservation expire | Idem |
| E, H11 | Chauffeur qui se désiste | Course reproposée aux autres chauffeurs, sans nouvelle demande ni nouveau paiement (déjà en place, UC24) | Service des courses |
| F | Satisfaction | Note de 1 à 5 ; taux de satisfaction = part des notes 4 ou 5, objectif 90 % | Statistiques (étape 7) |
| Q7, H17 | Réglages d'annulation (cahier des charges §7.4) | Annulation gratuite jusqu'au départ, aucun frais ensuite, annulation du chauffeur sans frais pour le passager : donc remboursement intégral dans tous les cas, comme aujourd'hui | Annulation (UC16), réglages de l'administrateur au P2 |
| – | Passager absent | Le chauffeur le signale après une attente de 10 minutes ; le passager est remboursé tant que la cliente n'a pas fixé de frais | États à demander à l'équipe BD (sprint 2) |
| H10 | Paiement | Simulé : un statut sur la course, pas de prestataire réel. Une table des paiements sera demandée à l'équipe BD si on branche le mode test d'un prestataire | Service de paiement |

### Gratuité et abonnement (entretien du 03/11)

| # | Sujet | Valeur provisoire | Où |
|---|---|---|---|
| – | Prix dans le démonstrateur | L'estimation reste calculée ; l'usager voit « reste à payer : 0 € » et n'a pas d'étape de paiement. À confirmer par les développeurs (autre choix : masquer tout prix) | Écran de confirmation, `ride_rules.price_cents`, service de paiement |
| – | Abonnement (60 € par mois, gratuit pour les structures affiliées) | Non codé avant la soutenance ; décrit comme une suite du projet. Ce qu'il couvre et qui le paie : question à la cliente | Tables à demander à l'équipe BD le moment venu |
| – | Rémunération des chauffeurs | Inconnue : question à la cliente. En attendant, « Mes revenus » (UC28) reste tel quel, sans commission | Revenus du chauffeur |

### Zone

| # | Sujet | Valeur provisoire | Où |
|---|---|---|---|
| H18 | Rayon de contrôle autour de Cayenne | 20 km autour du centre de Cayenne. Ce n'est pas la règle de la zone (ce sont les communes) : il rattrape seulement une position impossible, comme Kourou saisi avec « Cayenne ». Les « 5 km » de la visio couperaient une partie de Matoury (l'aéroport est à plus de 10 km) | `PILOT_ZONE_RADIUS_KM`, `services/place_service.py` |
| H18 | Rayon des offres pour un chauffeur | 10 km autour de sa position | `OFFER_RADIUS_KM`, `services/ride_rules.py` |
| – | Demande hors zone | Refusée (`422`) avec un message qui donne les communes desservies (exigence du cahier des charges, §18) | Validation des lieux |
| UC81 | Kourou | Hors pilote ; s'ajoutera comme une donnée de référence | `sql/schema-mvp.sql` (équipe BD) |

### Suites de l'audit de sécurité (02/11/2026)

| # | Sujet | Valeur provisoire | Où |
|---|---|---|---|
| F6 | Plafond de courses non terminées par usager | 1 immédiate + 3 programmées | `MAX_OPEN_IMMEDIATE_RIDES`, `MAX_OPEN_SCHEDULED_RIDES`, `services/ride_rules.py` |
| F10 | Motif du trajet visible du chauffeur sur une offre | Le comportement actuel est gardé jusqu'à la réponse ; le client doit dire si le chauffeur en a besoin (un trajet « santé » est une donnée sensible) | DTO des offres |

### Appareils, notifications, abonnement

| # | Sujet | Valeur provisoire | Où |
|---|---|---|---|
| Q14 | SMS | Simulés : écrits dans les logs, sans numéro ni contenu personnel | `sms_repository.py` |
| – | Contenus des nouveaux modules (services d'aide, offres types, questions du questionnaire, fiches pratiques) | Rédigés par nous, fictifs, puis validés par la cliente ; le cahier des charges prévoit qu'elle fournisse ou valide les contenus (§15) | Données factices des `repository/`, puis données de démo de l'équipe BD |
| – | Traductions (créole guyanais, créole haïtien, portugais du Brésil, anglais) | Anglais et portugais rédigés par nous ; les deux créoles demandés à la cliente ou à des locuteurs. Une langue sans relecture n'est pas montrée en démo | `FRONTEND/src/i18n/` |
| – | Illustration de l'accueil | **Provisoire** : un dessin SVG fait par les développeurs (route, lieu de travail, voiture, deux personnes dont une en fauteuil), quelques centaines d'octets, dans le bandeau de l'accueil du visiteur et de l'usager. À remplacer par l'illustration définitive (fournie par la cliente ou faite avec elle) | `FRONTEND/src/components/home/HomeIllustration.tsx` et sa copie dans `FRONTEND/index.html`, [charte graphique](charte-graphique.md) partie 9 |
| – | Licence du code | MIT, en attendant le choix de la cliente (licence libre ou cession) | Fichier `LICENSE` à ajouter |

---

## 4. Ce que ces décisions changent

À faire dans le code, chacun dans sa propre branche :

- **Commission (Q8)** : **en suspens** depuis l'entretien du 03/11 (plus de prix par course).
  Ne pas la coder avant de savoir comment les chauffeurs sont payés.
- **Gratuité (entretien du 03/11)** : « reste à payer : 0 € » et plus d'étape de paiement pour
  l'usager, selon le choix des développeurs (partie 3).
- **Marquage** : ajouter le commentaire `CHANGER_SELON_DECISION` sur les constantes déjà en place
  citées en partie 3 (tarif, plafonds, rayons, délais).
- **Photo du chauffeur** : l'afficher sur la page du trajet avec le prénom et la note (sprint 1).
- **Opérateur** : UC40 à UC43 et UC45 restent prévus, mais au palier P2 (réservation pour le
  compte d'une personne), donc après la soutenance ; UC44 reste dehors.

Ce que le cahier des charges ajoute (détail et sprints dans
[CLAUDE.md](../CLAUDE.md), « Ordre de développement ») :

- **Sprint 1, sans changement de base** : maquettes ; accueil par besoins ; offres d'emploi avec
  « Comment y aller ? » ; liens vers les formations ; annuaire et fiches pratiques ; refonte de
  l'accueil (illustration, couleurs) ; conditions d'annulation à l'écran de confirmation ;
  gratuité ; sélecteur de langue à 5 langues ; FAQ ; installation en une commande.
- **Sprint 2, demandes à l'équipe BD** (une issue `bd` chacune) : tables des offres d'emploi,
  des services d'aide et des fiches pratiques, des questionnaires et des plans d'action ;
  horaires autorisés ; zones
  réglables ; repère et nombre de passagers sur une course ; états « chauffeur arrivé » et
  « passager absent » ; paiement « échoué » ; auteur et heure de chaque étape d'une course ;
  pièces du chauffeur et leur date d'expiration ; demandes de suppression de compte et de rappel.
- **Sprint 3** : statut du trajet et offres mis à jour en direct (sans `driver:location`) ;
  accessibilité de base ; données de démo par script ; dossier conformité du palier P1 (registre simplifié des traitements, matrice des
  flux), fichier `LICENSE`, inventaire des dépendances.

À mettre à jour dans la documentation :

- [cas-d-utilisation.md](cas-d-utilisation.md) : statut de UC41, UC45, UC56 ; mini CV dans UC15 ;
  nouveaux cas du cahier des charges (horaires, zones, tarifs, suppression de compte, rappel) ;
  UC73 (notifications) et UC79 (abonnement, revenu le 03/11) reclassés.
- [contrat-api.md](contrat-api.md) : H9, H14, H19 décidées ; commission dans les revenus ;
  nouveaux états et routes du cahier des charges.
