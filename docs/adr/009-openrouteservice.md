# 009. OpenRouteService pour les adresses et la distance

- **Statut** : Acceptée
- **Date** : décidée le 02/11/2026 (réservation)
- **Voir aussi** : [contrat d'API](../contrat-api.md) (H13), [architecture.md](../architecture.md#base-de-données)

## Contexte

Le prix dépend de la distance **par la route**, et l'usager doit trouver son adresse. Le cahier
des charges recommande l'API Adresse publique, « couverture de la Guyane à vérifier », et
demande des outils gratuits.

## Décision

**OpenRouteService**, sur données OpenStreetMap : recherche d'adresses et distance par la route
chez un seul fournisseur, avec une offre gratuite. Appelé uniquement depuis
`repository/place_repository.py`. S'il ne répond pas : `503`, pas de prix. Sans clé
(`ORS_API_KEY` vide), des lieux factices et aucun appel à Internet (tests, CI). Les lieux
renvoyés sont signés, pour qu'un client ne puisse pas inventer une position.

## Alternatives écartées

- **API Adresse (Base Adresse Nationale)** : gratuite et officielle, mais elle ne calcule pas de
  distance par la route (il faudrait un second service), et sa couverture en Guyane est incertaine.
- **Google Maps** : excellente couverture, mais payant au-delà d'un quota et lié à une carte
  bancaire.
- **Distance à vol d'oiseau** : gratuite, mais fausse sur les routes de Guyane, donc un prix faux.

## Conséquences

- Les quotas gratuits et l'obligation de citer la source restent à vérifier sur le compte avant
  la mise en service. La page « À propos » cite déjà OpenStreetMap et OpenRouteService.
- L'appel réel n'a été testé qu'avec de fausses réponses : à valider avec une vraie clé.
- Changer de fournisseur ne touche qu'un fichier.
- Les adresses imprécises (cahier des charges, §3) demanderont un point déplaçable sur une carte
  ([015](015-leaflet-openstreetmap.md)).
