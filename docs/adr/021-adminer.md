# 021. Adminer pour consulter la base depuis le navigateur

- **Statut** : Proposée
- **Date** : 16/11/2026
- **Voir aussi** : [008](008-mysql.md), [README, partie 4](../../README.md#base-de-données-mysql-dans-docker)

## Contexte

Pour regarder ce que contient la base locale (comptes, courses, données de référence), il faut
aujourd'hui une console `mysql` dans le conteneur ou un client graphique (DBeaver, Workbench) à
installer et à configurer sur chaque poste. Les cinq membres de l'équipe, développeurs comme
équipe BD, n'ont pas tous le même poste, et l'équipe BD a besoin de vérifier ses vues et ses
migrations sans écrire de ligne de commande.

## Décision

Un service **Adminer** (image officielle `adminer`, version figée) dans `compose.yaml`, sur
`http://localhost:8081`. Il est derrière le profil `outils` : il ne démarre que si on le demande
(`docker compose --profile outils up -d adminer`), jamais avec `docker compose up` ni pendant
la démo. Comme la base, il n'écoute que sur `127.0.0.1`. On s'y connecte avec l'utilisateur et
le mot de passe du `.env` : il n'a pas plus de droits que le compte saisi.

Licence : Apache 2.0 ou GPL 2, au choix (outil de développement, non distribué avec
l'application). Aucun compte ni service externe.

## Alternatives écartées

- **phpMyAdmin** : même usage, mais une image environ dix fois plus lourde et une interface
  plus chargée, pour des fonctions dont on ne se sert pas.
- **Client graphique sur chaque poste** (DBeaver, MySQL Workbench) : reste possible, mais demande
  une installation et une configuration par personne ; rien à ajouter au dépôt.
- **Une route de l'API qui exécute du SQL** : contourne les couches et les droits de l'API
  ([002](002-couches-et-repositories.md)), et serait une faille si elle restait en place.

## Conséquences

- Une commande et une URL pour parcourir les tables, lancer une requête ou exporter.
- Adminer permet aussi de **modifier** les données : une modification à la main éloigne la base
  de `sql/demo-data.sql` (remise à zéro : README, partie 4). Le schéma ne se change jamais par
  Adminer : il passe par une migration de l'équipe BD.
- Outil de poste de développement uniquement : jamais exposé sur un réseau ni dans un
  environnement hébergé. Adminer a déjà eu des failles : monter la version figée quand une
  correction sort.
