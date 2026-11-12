# 020. Géoplateforme de l'IGN pour les lieux et la distance

- **Statut** : Proposée (remplacera [009](009-openrouteservice.md) une fois acceptée)
- **Date** : 12/11/2026
- **Voir aussi** : [009](009-openrouteservice.md) (OpenRouteService), [015](015-leaflet-openstreetmap.md) (carte), [012](012-objectif-regular-2g.md) (Regular 2G)

## Contexte

La fiche 009 a retenu OpenRouteService, mais il n'a jamais servi pour de vrai : `ORS_API_KEY`
est vide, donc l'application ne propose que des lieux factices. Il faudrait ouvrir un compte au
nom d'Ingeco ou de l'IUT, puis le remettre à la fin du projet (cahier des charges, §20).

Le cahier des charges recommande « l'API Adresse publique (couverture de la Guyane à
vérifier) + saisie de repère ». Il rappelle que les adresses sont souvent imprécises en Guyane
(§3) : on se repère à la mairie, à l'école ou à un quartier, plus qu'au numéro de rue.

Cette API Adresse fait désormais partie de la **Géoplateforme de l'IGN** (`data.geopf.fr`), qui
calcule aussi des itinéraires. On l'a essayée le 12/11/2026 :

| Essai | Résultat |
|---|---|
| Une rue (« rue Lallouette Cayenne ») | trouvée, score 0,98 |
| Un lieu-dit (« Cogneau-Lamirande ») | trouvé à Matoury, score 0,95 |
| Un repère, en cherchant adresses et lieux ensemble (« mairie matoury ») | la mairie de Matoury en premier |
| Des lieux de Cayenne (mairie, collèges, gare routière) | trouvés |
| CHU de Cayenne, agence France Travail | **non trouvés** |
| Distance par la route, Cayenne → Matoury | 12 km, 17 min |
| Adresse la plus proche d'un point | trouvée (« Avenue Élie Castor, Cayenne ») |

Limites annoncées par le serveur : 50 requêtes par seconde pour la recherche et 10 pour
l'itinéraire. Aucune clé, aucun compte.

## Décision proposée

Utiliser la **Géoplateforme** pour les trois besoins, toujours depuis
`repository/place_repository.py`, à la place d'OpenRouteService :

- **chercher un lieu** : `/geocodage/search` sur les index `address` et `poi`, pour trouver les
  rues, les lieux-dits et les repères (mairies, écoles), limité aux communes de Guyane ;
- **retrouver l'adresse d'un point** posé sur la carte : `/geocodage/reverse` ;
- **calculer la distance par la route**, qui fixe le prix : `/navigation/itineraire`.

On garde ce que la fiche 009 avait prévu :
- s'il ne répond pas : `503`, pas de prix ;
- les lieux renvoyés restent signés ;
- le texte tapé n'est jamais écrit dans les logs ;
- les tests et la CI ne font aucun appel à Internet. Faute de clé pour déclencher le mode
  factice, un réglage du `.env` le fera (nom à choisir dans la pull request).

La recherche ne suffit pas pour un lieu sans adresse. Les deux autres moyens prévus par le
cahier des charges restent nécessaires :
- **un repère écrit** pour le chauffeur (« devant la mairie, portail vert ») : une colonne en
  base, demandée à l'équipe BD (issue 53) ;
- **un point déplaçable sur la carte** : fiche 015.

## Alternatives écartées

- **OpenRouteService** (fiche 009) : un compte à ouvrir puis à transmettre, une clé à garder
  secrète, des quotas jamais vérifiés.
- **Nominatim**, le serveur public d'OpenStreetMap : sa politique d'usage interdit la recherche
  pendant la frappe et limite à une requête par seconde. Il ne calcule pas d'itinéraire.
- **Google Maps** : payant au-delà d'un quota et lié à une carte bancaire (§20).

## Conséquences

- Plus aucun compte ni clé pour les lieux et la distance. Le service est public et gratuit, et
  correspond à ce que recommande le cahier des charges.
- Quelques repères importants manquent (CHU, France Travail). Pour les couvrir, une courte
  liste de lieux utiles par commune, tenue à la main, pourrait compléter la recherche ; ce
  choix est à faire avec la cliente.
- La source est à citer : la page « À propos » mentionnera l'IGN et la Géoplateforme. La
  licence exacte et les conditions d'usage sont à relire avant d'accepter la fiche.
- Le prix dépendra du réseau routier de l'IGN plutôt que de celui d'OpenStreetMap : les
  distances peuvent changer un peu.
- Si la fiche est acceptée, mettre à jour : `place_repository.py` et ses tests, `.env.example`,
  le tableau « Comptes des services externes » du README, la page « À propos »,
  [passage-en-production.md](../passage-en-production.md), la partie Stack de `CLAUDE.md`, et
  passer la fiche 009 à « Remplacée par 020 ».
