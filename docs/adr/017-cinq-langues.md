# 017. Cinq langues, repli sur le français, traductions chargées à la demande

- **Statut** : Proposée (pull request du sélecteur de langue)
- **Date** : 07/11/2026
- **Complète** : [013](013-traductions-maison.md), qui reste valable (fichiers maison, `t()`, `tn()`)
- **Voir aussi** : [012](012-objectif-regular-2g.md), [decisions.md](../decisions.md) (« Traductions »)

## Contexte

À l'entretien du 03/11, la cliente demande cinq langues : français, créole guyanais, créole
haïtien, portugais du Brésil et anglais. La fiche 013 prévoyait une langue de plus seulement
quand la cliente en fournirait les textes, et exigeait qu'une langue ait **toutes** les clés.
Or :

- l'anglais et le portugais sont rédigés par nous (decisions.md) ; les deux créoles attendent
  des locuteurs, sans date ;
- chaque traduction complète pèse environ 6 Ko compressés : les mettre dans le paquet principal
  ferait payer ~12 Ko de plus à chaque usager, francophone ou non (~0,4 s en « Regular 2G »).

## Décision

- Les **cinq langues** sont dans le sélecteur, en bas de chaque écran. Chacune est écrite dans
  sa propre langue (« English », « Kreyòl ayisyen »), pour qu'une personne qui ne lit pas la
  langue affichée retrouve la sienne.
- Une langue peut être **incomplète** (type `PartialTexts`) : un texte qui lui manque s'affiche
  en français. Les deux créoles sont vides pour l'instant.
- L'anglais et le portugais sont **complets** (type `Texts` : TypeScript refuse une clé
  manquante ou en trop ; Vitest vérifie les `{valeurs}` de chaque texte).
- Une traduction complète est un **fichier à part**, téléchargé la première fois qu'on la
  choisit (`import()`), puis gardé par la PWA pour le hors ligne. Au démarrage, la langue
  choisie lors d'une visite précédente est téléchargée avant le premier écran ; sans réseau,
  l'application démarre en français.

## Alternatives écartées

- **Toutes les traductions dans le paquet principal** : plus simple, mais ~12 Ko compressés de
  plus pour tout le monde, et davantage à chaque nouvelle langue.
- **Ne montrer que les langues complètes** : les créoles, demandés par la cliente, seraient
  invisibles jusqu'à leur relecture.
- **i18next** : sait charger à la demande, mais ~20 Ko de plus (raisons de la fiche 013).

## Conséquences

- Le paquet principal ne grossit que des noms de langues et du sélecteur (~0,5 Ko compressé).
  Passer à l'anglais en « Regular 2G » prend ~0,8 s la première fois.
- Si le fichier d'une langue ne peut pas être téléchargé, la langue affichée ne change pas et
  un message le dit sous le sélecteur.
- Un écran en créole est aujourd'hui entièrement en français. Une langue sans relecture n'est
  pas montrée en démonstration (decisions.md).
- Les messages d'erreur métier du back restent en français (fiche 013) : en anglais ou en
  portugais, ils apparaissent en français. À traiter dans une prochaine fiche (codes d'erreur
  traduits par le front, ou langue envoyée au back).
- Le nom de l'application (« En route pour l'emploi ») n'est pas traduit : c'est un nom propre.
- Chaque nouveau texte de `fr.ts` doit aussi être écrit dans `en.ts` et `pt-BR.ts`, sinon
  TypeScript refuse la construction.
