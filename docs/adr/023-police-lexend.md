# 023. Une police web, Lexend, réduite à 18 Ko et jamais attendue

- **Statut** : Proposée (pull request de la refonte du design)
- **Date** : 24/11/2026
- **Voir aussi** : [010](010-react-vite-pwa.md) (CSS maison), [012](012-objectif-regular-2g.md) (Regular 2G)

## Contexte

L'interface était jugée « brute » : la police du téléphone change d'un appareil à l'autre et
donne un aspect de formulaire. La direction « Application » retenue le 24/11/2026 (maquettes de
l'accueil, trois directions) s'appuie sur une police plus ronde et plus lisible. Jusqu'ici, la
charte excluait toute police web pour tenir l'objectif « Regular 2G » (fiche 012) : sur ce
réseau, 1 Ko coûte environ 30 ms et chaque fichier ajoute un aller-retour.

## Décision

- **Lexend** (licence SIL Open Font License 1.1, [projet Lexend](https://github.com/googlefonts/lexend)),
  conçue pour la lecture par des personnes qui lisent difficilement.
- **Un seul fichier, hébergé par l'application** : `FRONTEND/src/assets/fonts/lexend-400-700.woff2`,
  18 Ko, avec sa licence à côté (`OFL-lexend.txt`). Police variable réduite aux graisses 400 à
  700 et aux caractères des cinq langues de l'interface (latin de base, accents, guillemets,
  euro). Aucun appel à Google Fonts ni à un autre service.
- **`font-display: optional`** : la police n'est utilisée que si elle est déjà là (cache, ou
  arrivée en moins de 100 ms). À la première visite en 2G, le texte s'affiche tout de suite dans
  la police du téléphone, sans page blanche ni saut quand la police arrive.
- **Gardée par le service worker** (`globPatterns` de `vite.config.ts`) : dès la deuxième
  ouverture, la police s'affiche sans attendre le réseau.

Mesuré le 24/11/2026 sur un serveur bridé à 250 kbit/s et 300 ms par requête : à la première
visite, la police part après le JavaScript (elle ne le retarde pas) et n'est pas affichée ; à la
réouverture, la page est affichée en 22 ms depuis le cache, en Lexend.

Pour refaire le fichier (nouvelle version de Lexend, caractère manquant), avec
[fontTools](https://github.com/fonttools/fonttools), à partir du fichier latin de
`@fontsource-variable/lexend` :

```
python -m fontTools.varLib.instancer lexend-latin-wght-normal.woff2 wght=400:700 -o lexend.ttf
python -m fontTools.subset lexend.ttf --flavor=woff2 --layout-features=kern,liga,calt --output-file=lexend-400-700.woff2 --unicodes="U+0020-007E,U+00A0-00FF,U+0152-0153,U+0178,U+02BC,U+2013-2014,U+2018-201E,U+2022,U+2026,U+2039-203A,U+20AC,U+2190,U+2192,U+2212,U+00B7,U+202F"
```

## Alternatives écartées

- **Rester sur la police du téléphone** : 0 Ko, mais l'aspect « brut » reste, et il change
  d'un téléphone à l'autre.
- **Atkinson Hyperlegible** (OFL, conçue pour la basse vision) : très lisible, mais plus sèche ;
  retenue dans la direction « Chaleureux », pas dans celle choisie.
- **Le paquet `@fontsource-variable/lexend` tel quel** : 40 Ko pour le latin complet, le double,
  et une dépendance npm de plus.
- **Google Fonts en ligne** : un service tiers de plus (§20), deux allers-retours de plus
  (feuille de style, puis police), et l'adresse IP de l'usager envoyée à Google.
- **`font-display: swap`** : la police remplace celle du téléphone quand elle arrive, ce qui fait
  sauter le texte pendant la lecture, sur le réseau le plus lent.

## Conséquences

- Première visite : apparence de la police du téléphone ; la mise en page doit rester correcte
  avec les deux polices (les tailles ne dépendent pas de la police).
- Un caractère hors de la liste (une langue nouvelle) s'affiche dans la police du téléphone :
  refaire le fichier avec la commande ci-dessus.
- La police est à ajouter à l'inventaire des dépendances (licence OFL 1.1, fichier modifié :
  réduit, nom conservé, aucun nom réservé dans la licence de Lexend).
