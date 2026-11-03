# Questions par sprint

Fiche pour l'oral, rangée dans l'ordre du développement : pour chaque sprint, ce qu'on y
développe, puis les questions dont on a besoin pour le faire.

**Règle** : le [cahier des charges v1.0](cahier-des-charges-v1.0.docx) est la source de vérité.
Ce qu'il fixe est appliqué sans question ([decisions.md](decisions.md#ce-que-fixe-le-cahier-des-charges-v10)).
On ne pose que ce qu'il ne tranche pas, ce qu'il laisse au choix de la cliente, ou ce qui reste
flou. Les points déjà tranchés sont dans [decisions.md](decisions.md) et ne sont pas repris ici.

Pour chaque question : à qui la poser (**Cliente**, **BD** pour l'équipe base de données,
**Enseignants**, **Interne** pour l'autre développeur), et la valeur appliquée sans réponse
(« Par défaut »). Noter la réponse, puis la reporter dans `decisions.md`.

Les questions de la revue du 03/11 et le parcours de démonstration sont aussi en PDF :
[questions-et-demo-2026-11-03.pdf](questions-et-demo-2026-11-03.pdf). L'ancienne liste
[questions-cliente-2026-11-04.pdf](questions-cliente-2026-11-04.pdf) est dépassée : la plupart de
ses questions sont tranchées par le cahier des charges.

## Le calendrier

Deux échéances :

- **Soutenance de la SAÉ : lundi 14 ou mardi 15/12/2026** (à confirmer). Environ 15 minutes ;
  chacun présente sa partie. La démo doit être prête et répétée avant.
- **Fin du projet pour la cliente : vers le 10/01/2027**. Le livrable est un **démonstrateur**
  documenté et transmis, pas un service en production (cahier des charges §1).

Le sujet de la SAÉ (IUT de Montreuil) demande un **prototype fonctionnel** et cite pour Ingeco :
création de comptes, réservation, géolocalisation des chauffeurs, suivi en temps réel, paiement
sécurisé, notifications, évaluation. Le cahier des charges met le suivi GPS en temps réel hors
périmètre : le « suivi en temps réel » est fait comme un **statut du trajet mis à jour en
direct**, et la géolocalisation sert à proposer au chauffeur les courses proches (décision du
03/11).

Notation : soutenance /20, rendu (rapport, base de données, code) /20, avis de la cliente /20.

| Sprint | Dates | Contenu |
|---|---|---|
| 1 | 04/11 → 17/11 | Manques du palier P1 **sans changement de base** : statut en direct, affectation par l'administrateur, refus d'une offre dans un délai, conditions d'annulation, choix de la langue, FAQ, installation en une commande ; commission |
| 2 | 18/11 → 01/12 | Vraie base MySQL, puis manques du P1 **qui demandent des colonnes** : horaires, zones et tarifs réglables, repère et passagers, « arrivé » et « absent », paiement échoué, pièces du chauffeur, suppression de compte, « Être rappelé » |
| 3 | 02/12 → 10/12 | Tableau de bord administrateur, dossier conformité, finitions ; **gel des fonctionnalités le 10/12** |
| – | 10/12 → 15/12 | Répétition de la démo, support de soutenance, rapport de gestion |
| 4 | 16/12 → 10/01 | Palier P2 selon le temps (bons solidaires, réservation pour le compte d'une personne), puis transmission |

**Règle : poser les questions d'un sprint au moins un sprint avant**, le temps que la réponse
arrive.

**Tout au long du projet** (exigé par le rapport de gestion) : noter le temps passé par chacun
sur ses tâches, et écrire un compte rendu de chaque réunion avec la cliente (au moins une
toutes les deux semaines).

---

## Le cahier des charges (v1.0)

Reçu le 03/11/2026 : [cahier-des-charges-v1.0.docx](cahier-des-charges-v1.0.docx) (version 1.0
du 14/10/2026). Sujet générique d'une « plateforme 360° d'accès à l'emploi » en dix modules
(M0 à M10) et trois paliers. Toutes les équipes doivent livrer le palier P1, qui couvre aussi
l'orientation, les offres d'emploi, les formations et l'annuaire. **À poser en premier** :

1. **Cliente** : avec deux développeurs et un gel le 10/12, pouvons-nous livrer le palier P1
   complet sur la mobilité (M4), le socle (M0) et l'administration (M9), sans l'orientation
   (M1), les offres d'emploi (M2), les formations (M3) ni l'annuaire (M5) ? Le scénario A
   (Jordan) se démontrerait à partir de la demande de trajet.
   *Par défaut : oui, P1 complet sur M0, M4 et M9.*
2. **Cliente** : quelle langue de démonstration voulez-vous, et quand pouvez-vous en fournir les
   textes ? Le cahier des charges prévoit que le porteur les fournit.
   *Par défaut : français seulement, avec le changement de langue en place.*
3. **Cliente** : licence libre (MIT ou EUPL 1.2) ou cession écrite des droits à Ingeco ? Une
   convention entre l'IUT, nous et Ingeco est-elle prévue ?
   *Par défaut : licence MIT.*
4. **Cliente** : nous autorisez-vous à afficher le nom et le logo d'Ingeco Territoires dans
   l'application ?
   *Par défaut : ni nom, ni logo.*
5. **Cliente** : la fiche de cadrage (§21) est à signer avant le premier sprint. Qui la remplit,
   et pour quand ?
   *Par défaut : nous la préremplissons pour le 10/11.*
6. **Cliente** : pourrez-vous assister à la soutenance, ou à une démonstration juste avant ?
7. **Enseignants** : quelle est la date exacte de la soutenance, le 14 ou le 15/12 ?
8. **Enseignants** : quel format pour le rapport de gestion (répartition des tâches, temps de
   chacun) ? Le travail fait entre la soutenance et le 10/01 compte-t-il dans la note ?
9. **BD** : la relecture du schéma v2 (`sql/`) peut-elle être finie pour le 17/11 ? Sinon, le
   branchement sur MySQL glisse, et la démo de décembre tourne sur des données factices.
10. **BD** : le cahier des charges demande des données que le schéma n'a pas encore. Pouvez-vous
    les ajouter au sprint 2 ? Horaires de service ; repère et nombre de passagers sur une
    course ; états « chauffeur arrivé » et « passager absent » ; paiement « échoué » ; auteur de
    chaque étape d'une course ; pièces du chauffeur et leur date d'expiration ; demandes de
    suppression de compte et de rappel. Une issue `bd` par besoin.
11. **BD** : qui présente quoi sur la base de données, à la soutenance ?

---

## Sprint 1 (04/11 → 17/11) : le palier P1 sans changement de base

**Ce qu'on fait :**
- Socket.IO : la page du trajet se met à jour seule (`ride:updated`), et les nouvelles courses
  arrivent seules chez les chauffeurs en ligne (`ride:offer`). Pas de position du chauffeur
  montrée au passager (suivi GPS hors périmètre).
- Affectation et réaffectation d'une course par l'administrateur, avec avertissement du passager.
- Proposition d'une course au chauffeur avec un délai de réponse ; il accepte ou refuse.
- Conditions d'annulation affichées avant l'envoi de la demande.
- Changement de langue (structure des traductions déjà en place), FAQ.
- Photo, prénom et note du chauffeur sur la page du trajet.
- Installation en une commande : le back et le front ajoutés à Docker Compose.
- À côté : la commission dans « Mes revenus ».

**Questions :**

1. **Interne** : qui prend quoi ? Par exemple, le temps réel et l'affectation d'un côté, la
   langue, la FAQ et Docker de l'autre.
2. **Interne** : comment note-t-on le temps passé par chacun, pour le rapport de gestion ? Un
   tableur partagé, ou les issues GitHub ?
3. **Cliente** : le chauffeur a-t-il besoin de connaître le motif du trajet (emploi, santé…)
   avant d'accepter une course ? Un trajet « santé » est une donnée sensible.
   *Par défaut : on le montre aujourd'hui. On propose de le cacher.*
4. **Cliente** : combien de temps un chauffeur a-t-il pour répondre à une proposition ?
   *Par défaut : 5 minutes, puis la course est proposée aux autres.*
5. **Cliente** : quel pourcentage la plateforme prend-elle sur chaque course ? Ce taux peut-il
   changer pendant le pilote ?
   *Par défaut : 10 %, un chiffre provisoire.* (Q8)
6. **Cliente** : peut-on faire tester l'application à un chauffeur sur place, en Guyane, avec
   l'un de vos partenaires (cahier des charges §14 : volontaires, accord écrit) ?
7. **BD** : la photo du chauffeur est-elle stockée en base ou en fichier ? (H19)
8. **BD** : si le taux de commission peut changer, il faudra une colonne sur `course` avec le
   montant reversé au chauffeur. On vous la demande après la réponse à la question 5.

---

## Sprint 2 (18/11 → 01/12) : vraie base, puis le palier P1 avec la base

**Ce qu'on fait :**
- On branche l'API sur la base MySQL de l'équipe BD, à la place des données factices. Le rendu
  de la SAÉ est noté avec la base de données, et l'équipe BD présente sa partie à la soutenance.
- Puis les manques du P1 qui demandent des colonnes (demandées au sprint 1, question 10) :
  horaires autorisés et refus expliqué hors horaire ; zones et tarifs réglables par
  l'administrateur ; repère et nombre de passagers ; étapes « chauffeur arrivé » et « passager
  absent » ; paiement échoué ; auteur et heure de chaque étape ; pièces du chauffeur et
  suspension à leur expiration ; demande de suppression de compte ; « Être rappelé » et
  signalement d'un problème.

**Questions :**

1. **BD** : MySQL 8.4 est-il confirmé ?
2. **BD** : pouvez-vous ajouter la colonne `version_session` sur `utilisateur`, et séparer
   `sql/demo-data.sql` ? (README, partie 5)
3. **Interne** : qui branche l'API sur MySQL ?
4. **Cliente** : quels horaires autoriser pour les demandes de trajet ?
   *Par défaut : à toute heure, tous les jours (le réglage existe, il ne bloque rien).*
5. **Cliente** : quand le passager est absent, combien de temps le chauffeur attend-il, et le
   passager est-il remboursé ?
   *Par défaut : 10 minutes d'attente, passager remboursé.*
6. **Cliente** : un usager peut-il avoir au plus 1 trajet immédiat et 3 trajets réservés à
   l'avance en même temps ?
   *Par défaut : oui.*

---

## Sprint 3 (02/12 → 10/12) : tableau de bord et gel avant la soutenance

**Ce qu'on fait :** un tableau de bord administrateur (demandes en attente, courses,
annulations, chauffeurs disponibles, cahier des charges §7.9) ; le dossier conformité du palier
P1 (registre simplifié des traitements, matrice des flux), le fichier `LICENSE` et l'inventaire
des dépendances ; on corrige les bogues et on fait le passage « Regular 2G » de tout le
parcours, puis **plus aucune nouvelle fonctionnalité après le 10/12**. Du 10 au 15/12 :
répétition de la démo, support de soutenance, rapport de gestion.

**Questions (à poser au sprint 1) :**

1. **Cliente** : la satisfaction, c'est la part des notes de 4 ou 5 sur 5, avec un objectif de
   90 %. D'accord ? (proposition F)
2. **Interne** : qui prépare le support de soutenance et le rapport de gestion, et qui présente
   quelle partie ?
3. **Interne** : la démo tourne-t-elle en local ou en ligne ? Une démo en ligne demande d'avoir
   choisi un hébergement gratuit avant le 10/12.

---

## Sprint 4 (16/12 → 10/01) : le palier P2, puis la transmission

**Ce qu'on fait :** selon le temps, des éléments du palier P2 dans le cadre du cahier des
charges : les bons solidaires (éligibilité validée par un prescripteur, plafond, enveloppe par
financeur, tiers payeur, codes de trajet), puis la réservation pour le compte d'une personne
avec son accord tracé (centre d'appel). Ensuite les livrables de transmission : guide
utilisateur, guide administrateur, vidéo de 5 minutes, note de transmission, remise des accès.

**Questions (à poser au sprint 2 ou 3) :**

1. **Cliente** : pour les bons, quels montants : plafond par personne, taux de réduction, taille
   des enveloppes de chaque financeur ?
2. **Cliente** : la personne du centre d'appel peut-elle annuler un trajet pour l'usager, et voir
   ses anciens trajets ?
   *Par défaut : annuler oui, voir les anciens trajets non (motif « santé »).* (Q2)
3. **Cliente** : quels sont les montants définitifs du tarif ?
   *Par défaut : 8 € de prise en charge + 0,80 € par kilomètre.* (Q10)
4. **Cliente** : quand faudra-t-il ajouter Kourou aux zones desservies ?
5. **Cliente** : à qui remettre les accès et le code le 10/01 : Ingeco, l'IUT, une autre
   promotion ?
6. **BD** : une table des paiements, si on branche un prestataire en mode test. (H10)
7. **Interne** : quel hébergement gratuit pour la démo, et qui regarde les options ?
8. **Interne** : qui vérifie les quotas gratuits d'OpenRouteService et l'obligation de citer la
   source ?
