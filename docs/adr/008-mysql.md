# 008. MySQL 8.4 plutôt que PostgreSQL et PostGIS

- **Statut** : Acceptée, confirmée par l'équipe BD le 03/11/2026 ([PR #36](https://github.com/DenisZAPOI/Ingeco/pull/36))
- **Date** : décidée le 20/10/2026 (schéma v2 et base locale dans Docker)
- **Voir aussi** : [README, partie 5](../../README.md#5-pour-léquipe-base-de-données), [002](002-couches-et-repositories.md)

## Contexte

La base appartient à l'équipe BD (parcours C), qui la conçoit et la présente à la soutenance. Le
cahier des charges recommande PostgreSQL, avec PostGIS pour les zones. Notre zone desservie est
pour l'instant une **liste de communes**, pas un tracé, et la distance par la route vient d'un
service externe ([009](009-openrouteservice.md)).

## Décision

**MySQL 8.4**, le système que l'équipe BD connaît, en local dans un conteneur Docker
(`compose.yaml`), pilote PyMySQL. Les tests tournent sur SQLite en mémoire.

## Alternatives écartées

- **PostgreSQL + PostGIS** : meilleur pour les calculs géographiques (zones dessinées, chauffeurs
  proches), mais l'équipe BD aurait dû apprendre un nouveau système pendant le projet, pour un
  besoin spatial qu'on n'a pas encore.
- **SQLite partout** : simple, mais pas fait pour plusieurs écritures en même temps en
  production.

## Conséquences

- SQLAlchemy cache presque toutes les différences : changer de système demanderait peu de code
  ([002](002-couches-et-repositories.md)).
- Si la cliente veut des zones dessinées sur une carte, MySQL a des types spatiaux suffisants
  pour des polygones simples ; au-delà, revoir ce choix dans une nouvelle fiche.
- À confirmer par l'équipe BD (question du sprint 2), avec l'hébergement de la base en production.
