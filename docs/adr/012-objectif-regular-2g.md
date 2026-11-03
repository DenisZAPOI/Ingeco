# 012. Objectif réseau « Regular 2G » pour chaque fonctionnalité

- **Statut** : Acceptée
- **Date** : décidée le 20/10/2026
- **Voir aussi** : [architecture.md](../architecture.md#réseau-faible--objectif-regular-2g)

## Contexte

Réseau inégal et données chères en Guyane (cahier des charges, §3). Le cahier des charges
demande un test en « 3G simulée » et vise moins de 1 Mo au premier chargement (P2). Mesuré le
20/10/2026 : sur un réseau faible, c'est le **nombre d'allers-retours** qui coûte le plus
(chacun prend au moins 300 ms), plus que le poids.

## Décision

Chaque fonctionnalité est vérifiée avec le profil **« Regular 2G »** des DevTools (250 kbit/s,
300 ms d'aller-retour) avant sa pull request : quelque chose d'utile à l'écran en moins de 1 s,
un écran utilisable en moins de 5 s à la première visite, une réouverture sans attente. Moyens :
écran d'accueil en HTML avant le JavaScript, chargement optimiste de la session, allers-retours
comptés, messages de réseau lent.

## Alternatives écartées

- **« 3G » seulement**, comme le cahier des charges : trop indulgent pour les zones les moins
  bien couvertes ; viser plus bas couvre aussi la 3G.
- **Un budget de poids seul** (par exemple 200 Ko) : ne voit pas les allers-retours en série,
  qui sont le vrai coût.

## Conséquences

- Une étape de test de plus par fonctionnalité, décrite dans architecture.md.
- Chaque nouvelle dépendance se justifie par son poids ; Leaflet sera chargé seulement sur
  l'écran de la carte.
