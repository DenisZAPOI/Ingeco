# 007. Limites, verrous et inscriptions en attente en mémoire

- **Statut** : Acceptée
- **Date** : décidée le 02/11/2026 (audit de sécurité, F5 et F15) ; verrous ajoutés le 03/11/2026
- **Voir aussi** : [architecture.md](../architecture.md#transitions-dune-course), [004](004-mots-de-passe-scrypt.md)

## Contexte

Plusieurs mécanismes ont besoin d'un état partagé entre les requêtes : les compteurs d'essais,
les inscriptions en attente de leur code, et des verrous pour qu'une vérification et l'écriture
qui suit ne se mélangent pas avec celles d'une autre requête (deux réservations parties en même
temps sur un réseau lent). La vraie base n'arrive qu'au sprint 2.

## Décision

Garder cet état **en mémoire du processus de l'API** : `utils/rate_limit.py`,
`repository/registration_repository.py`, `utils/locks.py` (un verrou par chauffeur ou par usager).
Les changements de statut d'une course restent protégés en base par des écritures
conditionnelles, qui marchent déjà avec plusieurs processus.

## Alternatives écartées

- **Redis** : la bonne réponse à plusieurs processus, mais un service de plus à installer et à
  héberger gratuitement.
- **Tables en base** : demandées à l'équipe BD pour des données de quelques minutes ; lourd pour
  le MVP.

## Conséquences

- **Valable pour un seul processus d'API.** Au déploiement : un seul processus, ou passer à Redis.
- Un redémarrage efface les inscriptions en attente (10 minutes au plus) et remet les compteurs à
  zéro.
- Avec MySQL, remplacer les verrous par `SELECT … FOR UPDATE` sur la ligne du chauffeur ou de
  l'usager, dans la même transaction.
