# Compte rendu : entretien avec la cliente du 03/11/2026

- **Date** : mardi 3 novembre 2026, après la réception du cahier des charges v1.0.
- **Source** : notes de Denis ZAPOI. À faire relire par la tutrice (Sophonie Delva) pour en garder
  une trace écrite.

## Ce qui prime

Ces réponses sont **postérieures au cahier des charges** et précisent ce que la cliente veut
vraiment pour son pilote. Sur les points qu'elles couvrent, elles priment sur le cahier des
charges, qui reste la source de vérité pour tout le reste. Elles sont reportées dans
[decisions.md](decisions.md#réponses-de-la-cliente-du-03112026-entretien).

## Décisions

| Sujet | Ce que la cliente a dit | Ce que ça change |
|---|---|---|
| Périmètre | On fait **tout le socle**, y compris l'emploi (et donc l'orientation, la formation, l'annuaire) | Confirme la décision interne du 03/11 : tout le palier P1 |
| Attribution des courses | **Ce n'est pas l'administrateur qui donne une course à un chauffeur.** Le **premier chauffeur disponible** la prend, depuis sa page qui liste les courses en attente autour de lui | C'est déjà le fonctionnement codé (offres proches, « Accepter », une course à un seul chauffeur). On retire du sprint 1 l'affectation et la réaffectation par l'administrateur, et le délai de réponse et le refus d'une proposition faite à un chauffeur précis |
| Langues | Il faudrait le **créole guyanais**, le **créole haïtien**, le **portugais du Brésil** et l'**anglais**, en plus du français | Sélecteur de langue avec ces 5 langues. Qui écrit et relit les traductions : à décider (voir plus bas) |
| Accueil | Mettre une **image** en rapport avec l'inclusion, le transport, le travail ; **plus de couleurs** ; un rendu **plus abouti**, en restant léger | Refonte de l'accueil et de la charte graphique (palette élargie, illustration). La charte interdisait jusqu'ici toute image décorative : la règle change pour l'accueil |
| Tarification | Pas un prix par course : un **abonnement mensuel, de l'ordre de 60 €**, qui donne droit aux courses. **Gratuit** pour une personne envoyée par une structure affiliée (par exemple France Travail). Pour l'instant, l'application ne sert **que dans la structure de la porteuse de projet** : donc **entièrement gratuite** | Pour le démonstrateur : aucun paiement demandé à l'usager. L'abonnement reste à concevoir (plus tard). Le paiement simulé par course et la commission ne collent plus au modèle |

## Questions qui restent

Pour les développeurs (décision interne) :

1. **Prix et paiement dans le démonstrateur** : on masque complètement le prix et l'étape de
   paiement, ou on affiche la valeur du trajet avec « Pris en charge, reste à payer : 0 € » ?
   (Le paiement simulé est déjà codé ; la SAÉ cite le « paiement sécurisé ».)
2. **Abonnement** : le simuler avant la soutenance (souscrire, voir ses droits), ou le décrire
   seulement comme une suite du projet ?
3. **Traductions** : qui les écrit (nous, avec relecture par la cliente ou des locuteurs), et
   quelles langues sont prêtes pour la démo ?
4. **Illustration de l'accueil** : dessin SVG fait par nous, illustration sous licence libre, ou
   photo fournie par la cliente ?

À poser à la cliente (revue du mardi ou WhatsApp) :

1. **Rémunération des chauffeurs** : s'il n'y a plus de prix par course, comment sont-ils payés
   (salariés de la structure, forfait, montant par course payé par la structure) ? Ça décide du
   sort de la commission (Q8) et de la page « Mes revenus ».
2. **Abonnement** : ce qu'il couvre (courses illimitées, un nombre de courses, une distance), qui
   le paie, et quelles structures sont « affiliées ».
3. **Traductions** : peut-elle fournir ou faire relire les textes en créole guyanais et en créole
   haïtien ?
4. **Image et couleurs** : a-t-elle une photo ou une identité visuelle à utiliser, et
   peut-on utiliser le nom et le logo d'Ingeco Territoires ?
