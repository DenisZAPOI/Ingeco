# 002. Couches contrôleur, service, repository ; SQLAlchemy

- **Statut** : Acceptée
- **Date** : décidée le 06/10/2026 (socle du projet)
- **Voir aussi** : [architecture.md](../architecture.md#règle-de-dépendance), [008](008-mysql.md)

## Contexte

La base de données est conçue et livrée par une autre équipe (trois étudiants du parcours C),
sur un calendrier différent du nôtre : le schéma v2 n'est validé qu'au 17/11/2026. Il fallait
développer tout le parcours de réservation avant d'avoir la vraie base, puis la brancher sans
tout réécrire. Le code doit aussi être transmissible à une autre équipe (cahier des charges, §1).

## Décision

Trois couches à sens unique : **contrôleur** (HTTP) → **service** (règles métier, droits,
transaction) → **repository** (seul endroit qui parle à la base ou à un service externe). Un
service ne connaît pas Flask ; un repository ne lève jamais d'erreur HTTP. Accès à la base par
**SQLAlchemy**, sans jamais créer de table depuis le code (`create_all()` interdit) : les modèles
suivent le schéma de l'équipe BD. En attendant la base, les repositories servent des données
factices en mémoire.

## Alternatives écartées

- **Logique dans les routes** : plus rapide au début, mais changer de source de données aurait
  touché tous les fichiers.
- **SQL brut partout** : précis, mais verbeux pour les requêtes simples. On garde du SQL explicite
  pour les requêtes fines, et les requêtes lourdes deviennent des vues SQL écrites par l'équipe BD.
- **ORM qui crée le schéma (migrations Alembic côté développeurs)** : contraire au partage des
  rôles, la base n'est pas à nous.

## Conséquences

- Les services se testent sans serveur ni base (tests sur SQLite en mémoire).
- Le branchement sur MySQL (sprint 2) ne change que `repository/` et `models/`.
- Plus de fichiers par fonctionnalité ; la liste de contrôle d'architecture.md, partie 3, guide
  l'ajout.
