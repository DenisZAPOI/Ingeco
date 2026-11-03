# 013. Textes dans des fichiers de traduction maison

- **Statut** : Acceptée
- **Date** : décidée le 03/11/2026, appliquée le 03/11/2026
- **Voir aussi** : [CLAUDE.md](../../CLAUDE.md) (« Règles du cahier des charges »), [012](012-objectif-regular-2g.md)

## Contexte

Le cahier des charges exige au palier P1 que tous les textes soient dans des fichiers de
traduction, et qu'on puisse changer de langue sur tous les écrans clés (la Guyane est très
plurilingue). Aujourd'hui, les textes sont écrits en français directement dans les composants.
Aucune autre langue n'est encore fournie par la cliente.

## Décision

Un fichier de textes typé par langue (en commençant par `fr.ts`) et une petite fonction `t()`,
**sans dépendance**. TypeScript refuse une clé qui n'existe pas. Les autres langues s'ajoutent
quand la cliente en fournit les textes.

## Alternatives écartées

- **i18next + react-i18next** : la référence (pluriels, chargement à la demande), mais environ
  20 Ko compressés de plus, pour des besoins simples.
- **FormatJS (react-intl)** : encore plus complet et plus lourd.
- **Attendre une deuxième langue** : chaque nouvel écran écrit en dur augmente le travail de
  reprise.

## Mise en œuvre

- `FRONTEND/src/i18n/fr.ts` : environ 330 textes rangés par domaine (`auth`, `booking`, `ride`,
  `driver`, `admin`…), avec des valeurs à remplir (`'Bonjour {name}'`).
- `t('home.greeting', { name })` et `tn('driver.rideCount', n)` (clés `_one` et `_other`, forme
  choisie par `Intl.PluralRules`). Clés et valeurs vérifiées par TypeScript ; une autre langue
  doit avoir toutes les clés (type `Texts`).
- La langue est mémorisée sur le téléphone (`localStorage.langue`), appliquée à `<html lang>`, aux
  formats (dates, prix) et à tous les écrans, redessinés d'un coup. Pas de sélecteur tant qu'il
  n'y a qu'une langue.
- Une langue `test` (développement seulement) met chaque texte entre crochets pour repérer un
  oubli ; absente de l'application construite.
- `npm run lint:texts` (dans la CI) refuse un texte écrit dans le code ; Vitest teste les
  traductions, les pluriels et le changement de langue ([016](016-vitest.md)).

## Conséquences

- Coût : environ 3,6 Ko compressés de plus pour l'application (les clés), soit à peu près
  0,1 s en « Regular 2G ».
- Un texte traduit ne doit jamais rester dans une constante de module : il ne suivrait pas un
  changement de langue. On écrit une fonction ou une liste de clés.
- Les messages d'erreur métier du back restent en français. Quand une deuxième langue arrivera,
  il faudra choisir entre des codes d'erreur traduits par le front et une langue envoyée au back.
- L'écran d'accueil recopié dans `index.html` (affiché avant le JavaScript) reste en français ;
  l'application le remplace dans la bonne langue en moins d'une seconde.
- Les phrases avec un mot en gras (un numéro de téléphone) sont coupées en deux clés : un
  traducteur doit garder l'ordre des morceaux.
- Les pluriels et formats complexes sont écrits à la main ; si ça devient lourd, revoir ce
  choix dans une nouvelle fiche.
