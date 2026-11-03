# Questions par sprint

Fiche pour l'oral, rangée dans l'ordre du développement : pour chaque sprint, ce qu'on y
développe, puis les questions dont on a besoin pour le faire. Les points déjà tranchés le 03/11
sont dans [decisions.md](decisions.md) et ne sont pas repris ici.

Pour chaque question : à qui la poser (**Cliente**, **BD** pour l'équipe base de données,
**Enseignants**, **Interne** pour l'autre développeur), et la valeur appliquée sans réponse
(« Par défaut »). Noter la réponse, puis la reporter dans `decisions.md`.

## Le calendrier

Deux échéances, pas une :

- **Soutenance de la SAÉ : lundi 14 ou mardi 15/12/2026** (à confirmer). Environ 15 minutes ;
  chacun présente sa partie. La démo doit être prête et répétée avant.
- **Fin du projet pour la cliente : vers le 10/01/2027**, pour un démarrage en janvier.

Le sujet de la SAÉ (IUT de Montreuil) demande un **prototype fonctionnel** qui réponde aux
objectifs fixés avec la cliente, et cite pour Ingeco : création de comptes, réservation,
géolocalisation des chauffeurs, suivi en temps réel, paiement sécurisé, **notifications**,
évaluation. Ce qui manque encore de cette liste passe en premier.

Notation : soutenance /20, rendu (rapport, base de données, code) /20, avis de la cliente /20.

| Sprint | Dates | Contenu | Questions à poser |
|---|---|---|---|
| 1 | 04/11 → 17/11 | Étape 4 : temps réel, carte, géolocalisation, **notifications** ; commission | **Demain** |
| 2 | 18/11 → 01/12 | Vraie base MySQL ; **bons ou écran opérateur** (au choix de la cliente) | **Demain** |
| 3 | 02/12 → 10/12 | Statistiques de base ; finitions ; **gel des fonctionnalités le 10/12** | Au sprint 1 |
| – | 10/12 → 15/12 | Répétition de la démo, support de soutenance, rapport de gestion | **Demain** (enseignants) |
| 4 | 16/12 → 10/01 | Ce qui reste (bons ou opérateur), mise en ligne, passation à la cliente | Au sprint 2 ou 3 |

**Règle : poser les questions d'un sprint au moins un sprint avant**, le temps que la réponse
arrive. Demain, on pose donc celles du sprint 1, du sprint 2 et des enseignants.

**Tout au long du projet** (exigé par le rapport de gestion) : noter le temps passé par chacun
sur ses tâches, et écrire un compte rendu de chaque réunion avec la cliente (au moins une
toutes les deux semaines).

---

## Demain en premier : les enseignants et la démo

1. **Enseignants** : quelle est la date exacte de la soutenance, le 14 ou le 15/12 ?
2. **Enseignants** : un paiement simulé (mode test, aucune carte débitée) suffit-il pour
   « paiement sécurisé » ?
3. **Enseignants** : des SMS simulés, écrits dans les journaux, et des notifications dans
   l'application suffisent-ils pour « notifications » ?
4. **Enseignants** : quel format attendez-vous pour le rapport de gestion (répartition des
   tâches, temps de chacun) ? Un modèle existe-t-il ?
5. **Enseignants** : le travail fait entre la soutenance et le 10/01 compte-t-il dans la note du
   rendu ? Quand faut-il rendre le code et le rapport ?
6. **Cliente** : la soutenance a lieu mi-décembre. D'ici là, on aura la réservation complète,
   le suivi sur carte et les notifications. **Que voulez-vous voir ensuite en priorité : les
   bons solidaires, ou l'écran du centre d'appel ?** L'autre viendra entre la soutenance et
   janvier.
   *Par défaut : les bons, si vous nous dites comment ils fonctionnent d'ici le 17/11 ; sinon
   l'écran du centre d'appel.*
7. **Cliente** : pourrez-vous assister à la soutenance, ou à une démo juste avant ?

---

## Sprint 1 (04/11 → 17/11) : temps réel, carte, notifications

**Ce qu'on fait :**
- Socket.IO : la page du trajet se met à jour seule (`ride:updated`), plus de bouton
  « Actualiser ».
- Les nouvelles courses arrivent seules chez les chauffeurs en ligne (`ride:offer`).
- Le chauffeur partage sa position, et l'usager voit le chauffeur arriver sur une carte Leaflet.
- La photo, le prénom et la note du chauffeur s'affichent sur la page du trajet.
- Un bouton ouvre l'application GPS du téléphone du chauffeur (UC25).
- **Notifications** (proposition, à valider) :
  - dans l'application, un bandeau avec une vibration à chaque changement : chauffeur trouvé,
    chauffeur en route, course démarrée, terminée, annulée ;
  - des SMS simulés quand l'application est fermée ou que le réseau ne suit pas (UC62) ;
  - pas de notification push du téléphone, trop lourde et peu fiable en application web sur
    iPhone.
- À côté : la commission dans « Mes revenus ».

**Questions :**

1. **Interne** : qui prend l'étape 4 ? On la découpe en deux, Socket.IO et les notifications
   d'un côté, la carte et la géolocalisation de l'autre ?
2. **Interne** : comment note-t-on le temps passé par chacun, pour le rapport de gestion ? Un
   tableur partagé, ou les issues GitHub ?
3. **Cliente** : à quels moments l'usager doit-il être prévenu ? Chauffeur trouvé, chauffeur
   arrivé, course terminée, annulation : est-ce suffisant ?
   *Par défaut : ces quatre moments, dans l'application, et par SMS simulé si elle est
   fermée.* (UC73, à faire passer dans le MVP)
4. **Cliente** : le profil du chauffeur montré au passager, c'est prénom, note et photo. Cela
   vous suffit-il ? *(déjà décidé chez nous, à faire confirmer)*
5. **Cliente** : le passager et le chauffeur voient le numéro de l'autre, seulement pendant la
   course. Est-ce acceptable ? Uber, lui, passe par un numéro relais. *(déjà décidé chez nous, à
   faire confirmer)*
6. **Cliente** : peut-on faire tester l'application à un chauffeur sur place, en Guyane, pour
   vérifier le GPS et la réception ? C'était votre principale inquiétude.
7. **Cliente** : quels téléphones ont les chauffeurs et les usagers, surtout Android ou aussi des
   iPhone ? Sur iPhone, partager sa position en arrière-plan marche mal dans une application
   web.
   *Par défaut : les deux, avec les tests faits d'abord sur Android.*
8. **Cliente** : le chauffeur a-t-il besoin de connaître le motif du trajet (emploi, santé…)
   avant d'accepter une course ?
   *Par défaut : on le montre aujourd'hui. On propose de le cacher.*
9. **Cliente** : sans chauffeur au bout de 15 minutes, l'usager est prévenu et remboursé. Si un
   chauffeur se désiste, la course est proposée aux autres sans que l'usager refasse sa demande.
   D'accord ? (propositions D et E)
   *Par défaut : oui, c'est ce qui est en place.*
10. **Cliente** : quel pourcentage la plateforme prend-elle sur chaque course ? Ce taux peut-il
    changer pendant le pilote ?
    *Par défaut : 10 %, un chiffre provisoire.* (Q8)
11. **BD** : la photo du chauffeur est-elle stockée en base ou en fichier ? (H19)
12. **BD** : si le taux de commission peut changer, il faudra une colonne sur `course` avec le
    montant reversé au chauffeur. On vous la demande après la réponse à la question 10.
13. **Interne** : relire et merger la PR #17 (`docs/decisions.md`).

---

## Sprint 2 (18/11 → 01/12) : vraie base, puis bons ou opérateur

**Ce qu'on fait :**
- On branche l'API sur la base MySQL de l'équipe BD, à la place des données factices. Le rendu
  de la SAÉ est noté avec la base de données, et l'équipe BD présente sa partie à la soutenance.
- Puis, selon le choix de la cliente (question 6 de la première partie) :
  - **les bons solidaires** : l'administrateur crée les structures et leurs référents, le
    référent émet des bons et suit leur consommation, l'usager utilise un bon à la réservation ;
  - **ou l'écran opérateur** : l'opérateur cherche un usager ou lui crée un compte, réserve à sa
    place et lui envoie un lien de paiement par SMS (simulé).

**Questions pour la vraie base, à poser demain :**

1. **BD** : la relecture du schéma v2 (`sql/`) peut-elle être finie pour le 17/11 ? Sinon, le
   branchement sur MySQL glisse, et la démo de décembre tourne sur des données factices.
2. **BD** : MySQL 8.4 est-il confirmé ?
3. **BD** : pouvez-vous ajouter la colonne `version_session` sur `utilisateur`, et séparer
   `sql/demo-data.sql` ? (README, partie 5)
4. **BD** : qui présente quoi sur la base de données, à la soutenance ?
5. **Interne** : qui branche l'API sur MySQL ?

**Questions pour les bons, à poser demain.** Sans ces réponses, les tables des bons ne peuvent
pas être créées. **Sans réponse le 17/11, on fait l'écran opérateur au sprint 2**, et les bons
passent après la soutenance.

6. **Cliente** : un bon, c'est un pourcentage sur un nombre de trajets, ou un budget en euros ?
   Exemple : « 50 % sur 10 trajets » ou « 100 € avec 15 € maximum par trajet ».
   *Par défaut : un pourcentage sur un nombre de trajets.* (Q5)
7. **Cliente** : un bon est-il donné à une personne précise, ou c'est un code que la structure
   distribue comme elle veut ?
   *Par défaut : les deux possibles.* (Q6)
8. **Cliente** : qu'est-ce que la structure qui paie voit de chaque trajet ?
   *Par défaut : la date, les communes et le montant. Ni le nom, ni l'adresse, ni le motif.*
   (Q12)
9. **Cliente** : une personne sans carte bancaire ne pourra voyager qu'avec un bon qui paie tout
   le trajet. Est-ce acceptable pour votre public ? (Q9)
10. **Cliente** : qui donne le statut d'usager prioritaire, et qu'est-ce qu'il apporte ? Une
    priorité pour avoir un chauffeur, un prix réduit, ou seulement l'accès aux bons ?
    *Par défaut : c'est l'administrateur qui le donne, et il ne change rien automatiquement.*
    (Q3, Q4)
11. **Cliente** : tout le monde a le même tarif, et l'aide passe par les bons. D'accord ?
    (proposition C)
12. **Cliente** : si un trajet est annulé, l'usager est-il toujours remboursé en entier, bon
    compris ? Même s'il annule cinq minutes avant ?
    *Par défaut : oui, toujours en entier, et le bon est rendu.* (Q7)

**Questions pour l'écran opérateur, à poser demain (au cas où il passe en premier) :**

13. **Cliente** : la personne du centre d'appel peut-elle annuler un trajet pour l'usager ?
    *Par défaut : oui.* (Q2)
14. **Cliente** : peut-elle voir les anciens trajets d'un usager ?
    *Par défaut : non, à cause du motif « santé ».* (Q2)
15. **Cliente** : pouvez-vous nous confirmer par écrit que des personnes sont dédiées aux appels,
    et que tout le monde peut réserver par téléphone ? On n'en a pas de trace écrite. (H3)
16. **Cliente** : un usager peut-il avoir au plus 1 trajet immédiat et 3 trajets réservés à
    l'avance en même temps, qu'il réserve lui-même ou par téléphone ?
    *Par défaut : oui.*

---

## Sprint 3 (02/12 → 10/12) : statistiques et gel avant la soutenance

**Ce qu'on fait :** un tableau de bord administrateur simple (contenu libre : trajets par jour,
par commune et par motif, note moyenne, taux de satisfaction). On corrige les bogues, on fait le
passage « Regular 2G » de tout le parcours, puis **plus aucune nouvelle fonctionnalité après le
10/12**. Du 10 au 15/12 : répétition de la démo, support de soutenance, rapport de gestion.

**Questions (à poser au sprint 1) :**

1. **Cliente** : la satisfaction, c'est la part des notes de 4 ou 5 sur 5, avec un objectif de
   90 %. D'accord ? (proposition F)
2. **Interne** : qui prépare le support de soutenance et le rapport de gestion, et qui présente
   quelle partie ?
3. **Interne** : la démo tourne-t-elle en local ou en ligne ? Une démo en ligne demande d'avoir
   choisi l'hébergement avant le 10/12.

---

## Sprint 4 (16/12 → 10/01) : le reste, et la mise en service

**Ce qu'on fait :** ce qui n'a pas été fait avant la soutenance (bons ou écran opérateur),
puis la mise en ligne pour le démarrage de janvier, et la passation à la cliente.

**Questions (à poser au sprint 2 ou 3) :**

1. **Cliente** : qui paie les frais de fonctionnement : l'hébergement, les vrais SMS, le
   prestataire de paiement ?
2. **Cliente** : pour s'inscrire, on envoie un code par SMS. D'accord, sachant que de vrais SMS
   auront un coût ?
   *Par défaut : oui.*
3. **Cliente** : quels sont les montants définitifs du tarif ?
   *Par défaut : 8 € de prise en charge + 0,80 € par kilomètre.* (Q10)
4. **Cliente** : le service tourne-t-il 24 h/24, ou en semaine avec des horaires élargis ? On
   peut demander un trajet à toute heure, et le prix ne change plus une fois annoncé : d'accord ?
   (propositions A et B)
   *Par défaut : l'application n'impose aucun horaire.*
5. **Cliente** : une demande en dehors de Cayenne, Rémire-Montjoly et Matoury : un message de
   refus suffit-il ? Et quand faudra-t-il ajouter Kourou ?
   *Par défaut : on refuse, avec un message qui donne les trois communes.*
6. **Cliente** : avez-vous un logo ou des couleurs à utiliser, et une nouvelle version du cahier
   des charges ?
7. **Cliente** : qui reprend l'application après le 10/01 (corrections, évolutions) ?
8. **BD** : où sera hébergée la base en production ?
9. **BD** : une table des paiements, si on branche un prestataire en mode test. (H10)
10. **Interne** : quel hébergement choisir, et qui regarde les options ?
11. **Interne** : qui vérifie les quotas gratuits d'OpenRouteService et l'obligation de citer la
    source ?

---

## Après le projet

1. **Cliente** : l'abonnement mensuel (un nombre de courses, ou un montant dépensé) doit-il être
   dans la première version, ou plus tard ?
   *Par défaut : plus tard.*
