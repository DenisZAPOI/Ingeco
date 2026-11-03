# 013. Textes dans des fichiers de traduction maison

- **Statut** : Acceptée, pas encore appliquée
- **Date** : décidée le 03/11/2026
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

## Conséquences

- Tous les écrans existants sont à reprendre : une pull request à part, mécanique.
- Les messages d'erreur du back sont aussi en français : il faudra choisir entre des codes
  traduits côté front et une langue envoyée au back.
- Les pluriels et formats complexes seront écrits à la main ; si ça devient lourd, revoir ce
  choix dans une nouvelle fiche.
