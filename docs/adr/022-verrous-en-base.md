# 022. Verrous par usager et par chauffeur dans MySQL (SELECT … FOR UPDATE)

- **Statut** : Proposée (remplace la partie « verrous » de [007](007-etat-en-memoire.md) une fois acceptée)
- **Date** : 17/11/2026
- **Voir aussi** : [007](007-etat-en-memoire.md), [008](008-mysql.md), [architecture.md](../architecture.md#transitions-dune-course)

## Contexte

Certaines vérifications lisent d'autres lignes que celle qu'elles écrivent : le nombre de courses
ouvertes d'un usager avant une réservation, l'horaire d'un chauffeur avant qu'il accepte, les
courses d'un compte avant sa suspension. L'écriture conditionnelle sur le statut ne protège qu'une
ligne. Deux requêtes parties en même temps sur un réseau lent pourraient donc passer la même
vérification (audit F15).

La fiche 007 avait mis un verrou par compte en mémoire de l'API (`utils/locks.py`), valable pour un
seul processus, en attendant la vraie base. Les courses sont maintenant lues et écrites dans MySQL.

## Décision

Verrouiller la **ligne du compte** dans `utilisateur` par `SELECT … FOR UPDATE`
(`user_repository.lock`), en **première instruction** de la transaction qui vérifie puis écrit :
réserver (l'usager), accepter (le chauffeur), modifier un compte (l'administrateur sur ce compte).
Les deux requêtes sur un même compte passent l'une après l'autre ; le verrou tombe au `COMMIT` ou
au `ROLLBACK`. `utils/locks.py` est supprimé.

En première instruction : InnoDB prend l'instantané de lecture de la transaction à la première
lecture ordinaire. Après le verrou, la transaction voit donc ce que l'autre requête vient
d'enregistrer.

## Alternatives écartées

- **Garder les verrous en mémoire** : moins de travail, mais faux dès qu'il y a deux processus
  d'API, et sans lien avec les transactions de la base.
- **Redis** : un service de plus à installer, pour un besoin que la base couvre déjà.
- **Isolation `SERIALIZABLE`** : trop large ; elle bloque aussi des lectures sans rapport.
- **Une contrainte en base** (au plus une course immédiate ouverte par usager) : la règle dépend de
  l'heure et du statut, et le plafond reste provisoire (audit, à confirmer avec la cliente).

## Conséquences

- Valable avec plusieurs processus d'API : une limite de moins au passage en production.
- Les compteurs d'essais et les inscriptions en attente restent en mémoire (fiche 007, choix du
  17/11/2026 : données de quelques minutes, sans table).
- Une requête qui attend un verrou attend au plus `innodb_lock_wait_timeout` (50 s par défaut),
  puis échoue. Les transactions verrouillées sont courtes, sans appel réseau externe, sauf le
  calcul de distance d'une réservation, borné à 5 s (`ORS_TIMEOUT_SECONDS`).
- Les tests tournent déjà sur MySQL 8.4 : le verrou y est réellement pris.
