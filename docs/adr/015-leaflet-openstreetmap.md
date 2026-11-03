# 015. Leaflet et OpenStreetMap pour la carte

- **Statut** : Proposée (étape 4, sprint 1)
- **Date** : –
- **Voir aussi** : [009](009-openrouteservice.md), [012](012-objectif-regular-2g.md), [014](014-socket-io.md)

## Contexte

Deux besoins de carte : suivre l'arrivée du chauffeur (demandé par la SAÉ, à confirmer avec la
cliente), et placer un point sur une carte quand l'adresse est imprécise (cahier des charges, §3 :
« saisie d'un repère, point déplaçable sur carte »). Le cahier des charges recommande
OpenStreetMap avec Leaflet ou MapLibre. Le réseau est faible : les fonds de carte pèsent lourd.

## Décision proposée

**Leaflet** avec les tuiles **OpenStreetMap**, chargé seulement sur les écrans qui ont une carte
(`React.lazy`). L'information est d'abord donnée en texte (« Votre chauffeur arrive dans
4 min »), la carte vient ensuite. Les tuiles déjà vues restent en cache.

## Alternatives écartées

- **MapLibre GL** : cartes vectorielles plus belles, mais une bibliothèque bien plus lourde et du
  WebGL, lent sur les téléphones d'entrée de gamme.
- **Google Maps** : payant au-delà d'un quota et lié à une carte bancaire.
- **Pas de carte, seulement du texte** : reste le secours, mais ne permet pas de placer un point
  sans adresse.

## Conséquences

- Environ 40 Ko compressés pour Leaflet, plus les tuiles : à mesurer en « Regular 2G ».
- Les tuiles du serveur public d'OpenStreetMap ont une politique d'usage (pas de forte charge) :
  suffisant pour la démonstration, un autre fournisseur sera à prévoir pour un vrai service.
- Crédit « © contributeurs d'OpenStreetMap » visible sur la carte.
