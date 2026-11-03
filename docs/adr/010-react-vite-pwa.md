# 010. React, Vite et PWA, CSS maison sans framework

- **Statut** : Acceptée
- **Date** : décidée le 06/10/2026 (socle) ; charte et CSS le 19/10/2026
- **Voir aussi** : [charte graphique](../charte-graphique.md), [012](012-objectif-regular-2g.md)

## Contexte

Le cahier des charges recommande une PWA (React, Vue ou Svelte, avec Vite) et exclut les
applications publiées sur les stores. Le public a des téléphones d'entrée de gamme, souvent
Android, sur un réseau faible : chaque kilo-octet de JavaScript se paie en secondes d'attente.

## Décision

**React 19 + TypeScript**, construit par **Vite**, en **PWA** installable (vite-plugin-pwa), avec
react-router-dom. Le style est un **CSS maison** fondé sur des variables (`styles/global.css`),
sans framework, décrit par la charte graphique. Le moins de dépendances possible : une
bibliothèque n'entre qu'avec l'étape qui en a besoin.

## Alternatives écartées

- **Svelte** : un paquet plus léger, mais nouveau pour l'équipe, et moins de personnes pour
  reprendre le code ensuite.
- **Framework CSS (Tailwind, Bootstrap, MUI)** : plus rapide à démarrer, mais plus de poids
  (surtout MUI), ou un balisage chargé de classes, pour une interface volontairement simple.
- **Application native (Android)** : hors périmètre du cahier des charges, et deux bases de code.

## Conséquences

- L'application s'installe depuis le navigateur, sans store, et peut afficher son accueil sans
  réseau.
- En PWA, la géolocalisation s'arrête quand l'application passe en arrière-plan : une limite
  pour le suivi du chauffeur ([014](014-socket-io.md)).
- Après une mise à jour, le service worker sert l'ancienne version jusqu'au rechargement suivant.
