# 003. Session en JWT dans des cookies HttpOnly, CSRF par double envoi

- **Statut** : Acceptée
- **Date** : décidée le 19/10/2026 (authentification)
- **Voir aussi** : [architecture.md](../architecture.md#authentification), [audit de sécurité](../audit-securite-2026-11-02.md)

## Contexte

Des téléphones modestes, parfois partagés, sur un réseau lent. Chaque aller-retour coûte au moins
300 ms ([012](012-objectif-regular-2g.md)). Il faut une session qui dure (personne ne veut
retaper son mot de passe à chaque trajet), qu'un script injecté ne puisse pas voler, et qu'on
puisse couper tout de suite (compte suspendu, mot de passe changé).

## Décision

Deux JWT posés par Flask-JWT-Extended dans des cookies **HttpOnly** : un jeton d'accès de
15 minutes, et un jeton de renouvellement de 30 jours limité à `/auth/refresh`. Protection CSRF
par **double envoi** : un cookie lisible recopié dans l'en-tête `X-CSRF-TOKEN` de chaque
écriture. Le compte est relu à chaque requête, avec un numéro de version de session qui augmente
à chaque nouveau mot de passe et à chaque suspension.

## Alternatives écartées

- **Jeton dans le `localStorage`** : lisible par n'importe quel script de la page (XSS).
- **Session côté serveur (cookie + table des sessions)** : simple et révocable, mais une table de
  plus à demander à l'équipe BD, et une lecture en base de plus à chaque requête.
- **Jeton long sans renouvellement** : impossible à couper avant son expiration.

## Conséquences

- Les cookies CSRF lisibles disent au front s'il y a une session sans appel réseau : aucun appel
  pour un visiteur, un seul pour un utilisateur connecté.
- Front et API doivent partager le même site (domaine parent) en production, sinon le front ne
  lit pas le cookie CSRF.
- Relire le compte à chaque requête coûte une lecture en base, acceptée pour pouvoir couper une
  session tout de suite.
- Appareil partagé (palier P3) : session plus courte et déconnexion automatique à prévoir.
