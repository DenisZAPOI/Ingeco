# 019. Audio des fiches pratiques par la synthèse vocale du téléphone

- **Statut** : Proposée (pull request des fiches pratiques)
- **Date** : 11/11/2026
- **Voir aussi** : [012](012-objectif-regular-2g.md) (Regular 2G), [018](018-contenus-traduits-par-le-back.md) (contenus traduits)

## Contexte

Le cahier des charges (§7.5, module M5, palier P1) demande des fiches « Comment faire ? » en
langage simple, **avec audio** : une partie du public lit difficilement. Les fiches sont des
contenus envoyés par l'API, en français, en anglais ou en portugais du Brésil (fiche 018), et le
réseau visé est le « Regular 2G » (fiche 012).

## Décision

- Un bouton « Écouter la fiche » fait lire la fiche par la **synthèse vocale du navigateur**
  (Web Speech API, `speechSynthesis`) : le titre, l'introduction, chaque étape avec son numéro,
  puis ce qu'il faut apporter. Le même bouton devient « Arrêter la lecture ».
- La lecture se fait dans la langue de la fiche (champ `language`), avec une voix du téléphone
  qui parle cette langue. **Sans voix pour cette langue, le bouton n'apparaît pas** : jamais une
  fiche portugaise lue par une voix française.
- Quitter la fiche arrête la lecture.
- Aucun fichier ni service : rien à télécharger, rien n'est envoyé hors du téléphone.

## Alternatives écartées

- **Fichiers audio enregistrés** (par la cliente ou des locuteurs) : la voix est meilleure et les
  créoles deviennent possibles, mais chaque fiche pèse plusieurs centaines de kilo-octets, trop
  lourd en « Regular 2G », et il faut réenregistrer à chaque changement de texte.
- **Service de synthèse vocale en ligne** (API d'un fournisseur) : voix de qualité égale partout,
  mais un service externe de plus (compte, quotas, coût possible, §20) et le texte de la fiche
  envoyé à un tiers.

## Conséquences

- La voix dépend du téléphone : qualité inégale, et certains appareils n'ont pas de voix pour
  une langue (le bouton est alors masqué).
- Les créoles n'ont pas de voix de synthèse : une fiche en créole, quand il y en aura, ne pourra
  pas être écoutée par ce moyen. Si la cliente le demande, des enregistrements pour quelques
  fiches remplaceraient cette fiche de décision par une nouvelle.
- À tester sur un vrai téléphone Android (Chrome) avant la démonstration : la liste des voix
  arrive parfois après le premier affichage (événement `voiceschanged`, géré).
