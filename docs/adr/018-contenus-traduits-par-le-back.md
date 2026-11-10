# 018. Contenus traduits par le back, selon la langue du téléphone

- **Statut** : Proposée (pull request des offres d'emploi)
- **Date** : 10/11/2026
- **Complète** : [013](013-traductions-maison.md) et [017](017-cinq-langues.md), qui ne traduisent que l'interface
- **Voir aussi** : [012](012-objectif-regular-2g.md), issues `bd` #48 (offres d'emploi) et #49 (services d'aide et fiches pratiques)

## Contexte

Les fiches 013 et 017 traduisent les **textes de l'interface**, rangés dans les fichiers du
front. Mais une partie de ce qui s'affiche est une **donnée** envoyée par le back : l'intitulé,
l'employeur et la description d'une offre d'emploi, et bientôt les services d'aide et les fiches
pratiques « Comment faire ? ». En anglais ou en portugais, une page d'offre mêlait des libellés
traduits et un contenu resté en français.

## Décision

- Le front envoie la langue choisie dans l'en-tête **`Accept-Language`** de chaque appel
  (`api/client.ts`). Le navigateur l'accepte sans requête CORS préalable : **aucun aller-retour
  de plus** en « Regular 2G ».
- Le back lit cette langue (`utils/language.py`) parmi celles dont il a des contenus (`fr`,
  `en`, `pt-BR`) et renvoie chaque contenu **dans cette langue, ou en français** quand il n'y a
  pas de traduction. Les trois textes d'une offre sont toujours dans la même langue.
- Chaque contenu dit dans quelle langue il est (champ `language`). Le front le met dans
  l'attribut `lang` des textes concernés, pour qu'un lecteur d'écran les lise avec la bonne voix
  quand c'est du français de repli.
- Le contenu gardé sur le téléphone (affiché d'avance, fiche 012) est gardé **avec sa langue** :
  après un changement de langue, la liste dans l'ancienne n'est pas montrée.
- Les créoles n'ont pas encore de contenus : un téléphone en créole reçoit le français, comme
  pour l'interface.
- En base : une table de traductions par contenu, jointe avec repli sur le français, demandée à
  l'équipe BD dans les issues #48 et #49. D'ici là, les traductions sont dans les données
  factices de `repository/`.

## Alternatives écartées

- **Toutes les langues dans chaque réponse** (`{ fr, en, pt-BR }`) : le changement de langue est
  immédiat, mais chaque réponse est environ trois fois plus lourde pour tout le monde.
- **Contenus traduits par le front** (clés dans `fr.ts`) : impossible pour des contenus qui
  viendront de la base et que l'administrateur pourra modifier.
- **Contenus seulement en français, signalés comme tels** : c'est le cas des vraies offres, mais
  la cliente veut une application utilisable dans les cinq langues (entretien du 03/11).

## Conséquences

- Les messages d'erreur métier du back restent en français (fiche 013) : ce mécanisme ne
  concerne que les contenus.
- Chaque nouveau contenu est écrit en français, puis traduit en anglais et en portugais par
  les développeurs, à faire relire comme l'interface.
- Les réponses dépendent de la langue : un cache partagé devrait tenir compte de
  `Accept-Language` (aujourd'hui, les réponses de l'API ne sont pas mises en cache, `no-store`).
- Un changement de langue recharge les contenus de l'écran affiché : un aller-retour.
