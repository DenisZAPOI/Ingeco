# Audit RGPD de la codebase (24/11/2026)

Relecture de tout le code (back, front, `sql/`, données de test) au regard du RGPD et de la loi
Informatique et Libertés. **Règle décidée le 24/11/2026 : quand le cahier des charges demande
quelque chose que le RGPD interdit ou rend risqué, on respecte le RGPD et on retire ou on ne fait
pas.** Complète la partie 2 de [reste-a-faire-2026-11-22.md](reste-a-faire-2026-11-22.md) et
l'[audit de sécurité du 02/11](audit-securite-2026-11-02.md).

Gravité : **Critique** = manquement au texte, à corriger avant la soutenance ; **Important** =
minimisation ou sécurité insuffisante ; **Mineur** = à améliorer ou à documenter.

## Résumé

| # | Gravité | Constat | Article |
|---|---|---|---|
| R1 | Critique | Le motif « santé » est collecté, mis d'office depuis un service de santé, et envoyé à tous les chauffeurs en ligne | art. 9, art. 5.1.c |
| R2 | Critique | Aucune information des personnes : pas de page « Vos données », rien à l'inscription | art. 12, 13, 14 |
| R3 | Critique | Droits des personnes non outillés : ni suppression du compte, ni copie des données | art. 15, 17, 20 |
| R4 | Critique | Aucune durée de conservation : tout est gardé sans limite, rien n'est purgé | art. 5.1.e |
| R5 | Important | Adresses exactes de départ et d'arrivée montrées à tous les chauffeurs avant acceptation, et gardées à vie dans leur historique | art. 5.1.c, art. 25 |
| R6 | Important | Le questionnaire garde toutes les langues parlées alors que seul « parle français ? » sert : indice d'origine | art. 5.1.c, CDC §12 |
| R7 | Important | La déconnexion ne vide pas les brouillons (adresses, motif, réponses du questionnaire) | art. 32 |
| R8 | Important | Registre des traitements et analyse d'impact (AIPD) absents | art. 30, art. 35 |
| R9 | Mineur | Le bouton « Itinéraire » du chauffeur envoie la position du passager à Google | art. 44, art. 5.1.c |
| R10 | Mineur | Demandes de rappel sans compte : le numéro est gardé sans fin et aucun écran ne les traite | art. 5.1.b, 5.1.e |

## Décisions du 24/11/2026

Tous les constats R1 à R7, R9 et R10 sont à corriger avant l'arrêt du code (30/11), avec ces choix :

| # | Décision |
|---|---|
| R1 | Motif « santé » **retiré** (l'API le refuse, le front ne le propose plus, « Comment y aller ? » depuis un service de santé met « Autre ») **et** le chauffeur ne voit plus jamais le motif. Pas d'issue BD : la valeur `'sante'` reste dans l'ENUM, sans usage |
| R2 | Page « Vos données » ; responsable désigné par un texte neutre (« l'association porteuse du projet ») marqué `CHANGER_SELON_DECISION`, en attendant l'accord de la cliente pour son nom |
| R3 | « Supprimer mon compte » **enregistre une demande**, traitée par un administrateur qui clique « Anonymiser » (anonymisation de la migration 025). « Mes données » : une page lisible et un fichier JSON à télécharger |
| R4 | Durées du tableau R4 ; après 1 an, adresses et repères remplacés par la commune, coordonnées arrondies à 2 décimales (environ 1 km), sans changement de schéma |
| R5 | Communes et distances sur l'offre, adresses exactes après acceptation et jusqu'à la fin de la course, communes seulement dans l'historique du chauffeur |
| R6 | La question des langues devient « Êtes-vous à l'aise en français ? » (oui, un peu, non) |
| R7 | Brouillons vidés à la déconnexion |
| R9 | Lien `geo:` (application GPS choisie par le chauffeur sur Android), repli vers OpenStreetMap |

Découpage : `fix/rgpd-minimisation` (R1, R5, R6, R7, R9), puis `feature/vos-donnees` (R2, R3, R4, R10).

## Ce qui est déjà conforme

- **Logs** (`utils/logs.py`, `utils/request_logs.py`) : identifiant seulement, jamais de nom,
  téléphone, adresse, position, corps de requête ni chaîne de requête ; SMS simulés sans numéro ni
  code (`repository/sms_repository.py`).
- **Champs interdits** (§12) : aucun en base, dans les DTO ou les formulaires. Les besoins du
  questionnaire sont des besoins (« garde », « véhicule adapté »), jamais un diagnostic.
- **Position du chauffeur** : seule la dernière est gardée, effacée quand il passe hors ligne
  (`user_repository.set_availability`), jamais montrée au passager.
- **Pièces du chauffeur** : vérifiées en personne, seuls le type et la date d'expiration sont
  gardés (migration 024).
- **Contacts** : téléphone du passager, téléphone et photo du chauffeur visibles seulement pendant
  la course (`ride_service.present`, `driver_photo`).
- **Questionnaire sans compte** : rien n'est gardé (`orientation_service.preview`). Pas de décision
  automatique, contact humain dans chaque plan (art. 22).
- **Cookies** : seulement ceux de la session (`HttpOnly`), strictement nécessaires, donc sans
  bandeau de consentement. Aucun traceur, aucune police ni script tiers chargé par le front ;
  OpenRouteService est appelé par le back, l'adresse IP du téléphone ne lui parvient pas.
- **Téléphone partagé** : l'indice de session ne garde que le prénom et le rôle
  (`lib/sessionHint.ts`), les réponses de l'API ne sont pas mises en cache par la PWA.
- **Compte supprimé** : l'anonymisation est prévue en base (migration 025) et décidée
  ([decisions.md](decisions.md)), il manque la route (R3).
- **Données de test** (`sql/demo-data.sql`) : fictives, noms « Démo ».
- **Mots de passe** hachés en scrypt, codes jamais en clair (ADR 004).

## Constats

### R1. Motif « santé » (Critique)

**Où.** `dtos/ride_dto.py:19` (`Purpose`), `services/ride_rules.py:12`,
`FRONTEND/src/lib/ride.ts:8` ; `FRONTEND/src/lib/helpServices.ts:97` met le motif `health` **d'office**
quand on demande un trajet depuis un service d'aide de la catégorie santé ; `RideDto.purpose` est
envoyé dans les offres (`GET /drivers/me/ride-offers`), dans `GET /rides/{id}` d'une course en
attente pour tout chauffeur en ligne (`ride_service._may_see`) et affiché par
`pages/DriverRidePage.tsx:69`.

**Problème.** « Trajet santé » rattaché à une personne nommée est une **donnée de santé** (art. 9) :
traitement interdit sauf exception (consentement explicite, etc.), qu'on n'a pas. Il est envoyé à
des chauffeurs qui n'en ont aucun besoin pour conduire. La liste de motifs du cahier des charges
(§7.4) ne contient d'ailleurs pas la santé.

**Correction proposée.**
1. Retirer `health` des motifs acceptés par l'API (`422` s'il est envoyé) et proposés par le front ;
   « Comment y aller ? » depuis un service de santé met le motif « Autre ».
2. Ne plus envoyer `purpose` au chauffeur, ni sur une offre ni après acceptation : il ne lui sert
   pas. Le passager et le personnel le voient toujours.
3. Demande à l'équipe BD (issue `bd`) : retirer `'sante'` de l'ENUM `course.motif` et de la vue
   `stats_courses_par_motif` (migration 005), après reprise des lignes existantes en `'autre'`.

Même sans motif, l'adresse d'arrivée d'un centre de santé renseigne sur la santé : voir R5.

### R2. Information des personnes (Critique)

**Où.** Aucune page ni texte sur les données, hors une phrase avant le questionnaire
(`i18n/fr.ts`, `orientation.introPrivacy`). Rien sur les écrans d'inscription, « Être rappelé »,
réservation.

**Problème.** L'art. 13 impose de dire, au moment de la collecte : qui est responsable, pour quoi,
sur quelle base, à qui les données vont, combien de temps, quels droits et comment les exercer,
le droit de saisir la CNIL.

**Correction proposée.** Une page « Vos données » en langage simple (dans les 5 langues), liée
depuis le pied de page, l'inscription, « Être rappelé » et le questionnaire. Le responsable de
traitement réel est Ingeco Territoires : dans le démonstrateur, la page le dit et précise que les
données sont fictives. Destinataires à citer : chauffeur de la course, personnel (opérateur,
administrateur), OpenRouteService (adresses tapées, sans nom).

### R3. Droits des personnes (Critique)

**Où.** Aucune route : pas de `POST /users/me/deletion-request` (table `demande_suppression`
livrée, migration 002), pas d'export.

**Problème.** Droit à l'effacement (art. 17, aussi exigé au P1 §6), droit d'accès et à la
portabilité (art. 15, 20). Sans outil, la seule voie est une demande à la main.

**Correction proposée.**
- « Supprimer mon compte » dans le profil → demande enregistrée, traitée par l'administrateur avec
  l'anonymisation déjà décidée (statut `supprime`, nom et courriel effacés, textes libres effacés,
  courses gardées sans identité).
- « Télécharger mes données » : un fichier JSON avec le compte, les trajets, les réponses et le plan.

### R4. Durées de conservation (Critique)

**Où.** Aucune purge dans `utils/periodic.py`. `demande_aide` « jamais supprimée »
(`models/support.py`), chaque nouveau questionnaire **s'ajoute** aux anciens
(`orientation_repository.save`), courses avec adresses exactes gardées sans fin.

**Problème.** Art. 5.1.e : une donnée n'est gardée que le temps nécessaire, avec une durée fixée
à l'avance.

**Correction proposée** (durées à faire valider, valeurs provisoires dans `decisions.md`) :

| Donnée | Durée proposée | Comment |
|---|---|---|
| Ancien questionnaire et son plan | Supprimé dès qu'un nouveau est rempli | Dans la même transaction que l'enregistrement |
| Demande de rappel ou signalement | 3 mois après traitement | Tâche périodique |
| Adresses exactes et repères d'une course | 1 an après la fin, puis remplacés par le nom de la commune | Tâche périodique ; les communes suffisent aux statistiques |
| Commentaire d'évaluation | Comme la course | Idem |
| Compte inactif | 2 ans sans connexion, puis anonymisé après un SMS de prévenance | Après la soutenance (P2) |
| Logs | Selon l'hébergement (sortie standard) : 6 mois à 1 an | À écrire dans `passage-en-production.md` |

### R5. Adresses exactes visibles de tous les chauffeurs (Important)

**Où.** `driver_service.list_offers` → `OfferDto.ride` (adresses complètes, repères),
`ride_service._may_see` pour une course en attente ; historique du chauffeur
(`GET /rides?when=past`) avec les adresses de tous ses anciens passagers.

**Problème.** Tous les chauffeurs en ligne voient l'adresse du domicile et de la destination de
chaque passager, alors qu'un seul prendra la course (minimisation, protection dès la conception,
art. 25). L'adresse d'arrivée peut révéler une donnée sensible (centre de santé, association).

**Correction proposée.** Avant acceptation : commune de départ, commune d'arrivée, distance du
trajet et distance jusqu'au départ, horaire, besoin d'un véhicule adapté, nombre de passagers.
Adresses exactes et repères **après** acceptation, et seulement jusqu'à la fin de la course ; dans
l'historique du chauffeur, les communes seulement.

### R6. Langues parlées dans le questionnaire (Important)

**Où.** `orientation_rules.py` : `SpokenLanguage` (fr, gcr, ht, pt, es, en, nenge, autre), toutes
gardées dans `reponse_questionnaire` ; seule « parle français ou non » sert au plan
(`_needs_french_lessons`).

**Problème.** Garder « parle haïtien, nenge » sert d'indice d'origine, champ interdit par le cahier
des charges (§12) et proche de l'art. 9 (origine ethnique), sans usage.

**Correction proposée.** Remplacer la question par « Êtes-vous à l'aise en français ? » (oui / un peu
/ non), ou ne plus garder les langues (calculer le plan avec, puis ne garder que la réponse
« français »). La langue de l'interface reste un réglage du téléphone, pas une donnée du compte.

### R7. Brouillons gardés après la déconnexion (Important)

**Où.** `context/SessionProvider.tsx` (`logout`) n'efface ni `booking-draft` (adresses, motif) ni
le brouillon du questionnaire (`lib/orientation.ts`) dans le `sessionStorage`.

**Problème.** Sur un téléphone partagé (cas fréquent du public visé), la personne suivante voit les
adresses et les réponses de la précédente tant que l'onglet reste ouvert (sécurité, art. 32).

**Correction proposée.** Vider les deux brouillons à la déconnexion et quand l'API dit que personne
n'est connecté.

### R8. Registre et analyse d'impact (Important, hors code)

Le registre des traitements (art. 30) est dans le reste à faire. Une **AIPD** (art. 35) est
probablement obligatoire au passage en production : la CNIL l'exige dès deux critères, et on en
réunit au moins trois (personnes vulnérables, données sur la situation sociale et professionnelle,
localisation des chauffeurs, croisement de données). Pour le démonstrateur (données fictives) :
écrire le registre, et noter l'AIPD comme préalable obligatoire dans
[passage-en-production.md](passage-en-production.md).

### R9. Lien Google Maps (Mineur)

**Où.** `lib/geo.ts:20` (`directionsUrl`), bouton « Itinéraire » du chauffeur.

**Problème.** Un clic envoie à Google (États-Unis) les coordonnées du domicile du passager. Transfert
encadré (Data Privacy Framework) et à l'initiative du chauffeur, mais évitable.

**Correction proposée.** Lien `geo:lat,lng` (ouvre l'application GPS choisie par le chauffeur sur
Android), avec repli vers OpenStreetMap, ou garder Google et le citer dans la page « Vos données ».

### R10. Demandes de rappel sans compte (Mineur)

**Où.** `POST /support/callback` enregistre un numéro (même sans compte) ; aucun écran du personnel
ne liste ces demandes.

**Problème.** On collecte un numéro pour un rappel que personne ne peut faire depuis l'application
(finalité non servie), et on le garde sans fin (R4).

**Correction proposée.** Liste des demandes pour l'opérateur et l'administrateur avec « Traitée »,
puis purge à 3 mois (R4). À défaut, le dire comme limitation.

## Points vérifiés sans correction

- `needs_accessible_vehicle` : un besoin, pas un diagnostic ; nécessaire au chauffeur. À citer dans
  la page « Vos données ».
- Texte libre des expériences, commentaires d'incident et de signalement : peuvent recevoir une
  donnée sensible malgré la consigne. L'écran le rappelle ; effacés avec le compte (migration 025).
- `schema-hors-scope.sql` (`document_chauffeur.chemin_fichier`) : non chargé. S'il l'est un jour,
  il contredit la décision « pièces vérifiées en personne, rien de stocké ».
