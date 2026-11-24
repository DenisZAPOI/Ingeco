# Guide pour l'équipe base de données

Pour les trois membres de l'équipe BD : comment l'API se branche sur votre base, et ce dont les
développeurs ont besoin de votre part. Pour lancer la base en local : [developpement.md](developpement.md#base-de-données-mysql-dans-docker).

**Pour concevoir le schéma, partir de [contrat-api.md](contrat-api.md)** : il liste les données que
l'API lit et écrit, route par route.

## Le principe : le dossier `sql/` est à vous

- **Tout ce qui est dans `sql/` est à vous** : le schéma, les migrations, les données de
  référence, les index et les vues. Les développeurs n'y touchent plus (décidé le 03/11/2026),
  sauf les données de test `sql/demo-data.sql`, qu'ils écrivent depuis le 12/11/2026.
- **Les développeurs ne créent ni ne modifient jamais une table.** L'API se contente de lire et
  d'écrire dans les tables que vous avez créées.
- Si une fonctionnalité demande une nouvelle table ou colonne, les développeurs vous envoient une
  **demande écrite** (issue GitHub, [plus bas](#demander-un-changement-de-schéma)). C'est vous qui
  décidez et qui écrivez la migration.
- Ces fichiers font partie du **rendu noté de la SAÉ**, et c'est vous qui les présentez à la
  soutenance.

## Qui fait quoi

| Sujet | Équipe BD | Développeurs |
|---|---|---|
| Schéma (`sql/schema-mvp.sql`, `sql/schema-hors-scope.sql`) | Écrit, relu, validé | Lisent ; demandent un changement par écrit |
| Migrations (`sql/migrations/`) | Écrites et appliquées | Jamais |
| Données de référence (communes, tarif, types de trajets…) | Écrites | Demandent une valeur si besoin |
| Données de test (`sql/demo-data.sql`) | Relisent si elles le souhaitent | Écrites, personnes fictives (aussi chargées par les tests) |
| Index et contraintes | Écrits (à partir de [contrat-api.md](contrat-api.md), partie 6.6) | Signalent une requête lente |
| Requêtes lourdes (statistiques, chauffeurs proches, consommation des bons) | Écrites, en **vues SQL** | Lisent la vue depuis `repository/` |
| Requêtes courantes (lire un compte, créer une course…) | Relisent si elles le souhaitent | Écrites en Python (SQLAlchemy) dans `repository/` |
| Classes Python qui décrivent vos tables (`BACKEND/app/models/`) | – | Écrites, en suivant exactement votre schéma |
| Chargement de la base locale (partie base de `compose.yaml`) | Ajoutent les lignes de leurs fichiers | Ne la changent pas sans vous |

## Les migrations

Tant que personne n'a de vraies données, on peut effacer la base et la recréer. Une base en
service, elle, se **modifie** : c'est le rôle des migrations.

- **Le point de départ** est `sql/schema-mvp.sql` (version 2, validée le 03/11/2026). **On ne le
  modifie plus.**
- **Chaque changement** est un nouveau fichier `sql/migrations/NNN_ce_qu_il_fait.sql`, numéroté
  sur trois chiffres, **un changement par fichier**, en SQL MySQL, appliqué dans l'ordre.
- **Un fichier déjà mergé ne se modifie jamais** : une erreur se corrige par une nouvelle
  migration. Sinon, deux bases qui ont appliqué deux versions du même fichier divergent.
- **En tête de chaque fichier**, en commentaire : la date, l'auteur, l'issue liée, et comment
  revenir en arrière.

  ```sql
  -- 001 : colonne version_session sur utilisateur
  -- 05/11/2026, équipe BD, issue #21 (audit de sécurité, F3)
  -- Retour arrière : ALTER TABLE utilisateur DROP COLUMN version_session;
  ALTER TABLE utilisateur ADD COLUMN version_session INT NOT NULL DEFAULT 0;
  ```

- **Une base neuve** est créée par `sql/charger-base.sh` : schéma, migrations, puis données de
  test. Une erreur SQL arrête la création (`docker compose logs db` pour la voir).
- **Une base existante** reçoit les nouvelles migrations sans être effacée (issue #82) :
  `sql/migrer.sh`, lancé par le service `db-migrate` à chaque `docker compose up`, applique celles
  qui manquent dans la table `migration_appliquee` et note chacune après son succès. Attention :
  MySQL valide chaque `CREATE` ou `ALTER` aussitôt ; une migration de plusieurs instructions qui
  échoue au milieu peut en laisser une partie appliquée. Réparer alors à la main (retour arrière
  en tête du fichier), puis relancer.
- **Toujours tester une migration sur une base existante**, pas seulement sur une base neuve :
  `docker compose up -d db-migrate`, puis `docker compose logs db-migrate`.
- Les développeurs suivent chaque migration dans leurs classes Python : annoncez-la avant de la
  merger. Les tests automatiques (`pytest`, CI) construisent une base depuis vos scripts : une
  migration qui ne passe pas les fait échouer, et `tests/test_models.py` signale toute colonne
  qui ne correspond plus aux classes de `BACKEND/app/models/`.

## Les requêtes lourdes, en vues SQL

L'API écrit ses requêtes courantes en Python. Les **requêtes lourdes** vous reviennent :

| Requête | Pour | État |
|---|---|---|
| Statistiques : trajets par jour, par commune, par motif, notes | Tableau de bord administrateur (UC56) | Livrées (migrations 003 à 006) |
| Chauffeurs en ligne les plus proches d'un point | Proposer une course (contrat 6.1) | Livrée (migration 007) |
| Consommation des bons par structure | Suivi des référents (contrat 6.4) | Avec les tables des bons (P2) |

**Livrez-les en vues** (`CREATE VIEW`), chacune dans une migration. L'API lit une vue comme une
table : la requête reste dans vos fichiers, testable directement dans MySQL.

## Comment l'API parle à la base

L'API utilise **SQLAlchemy** : le code décrit les requêtes en Python, et SQLAlchemy les traduit
en SQL. `select(Ride).where(Ride.status == "en_attente").limit(10)` devient
`SELECT ... FROM course WHERE statut = 'en_attente' LIMIT 10`. Pour chaque table, les développeurs
écrivent une classe dans `BACKEND/app/models/` qui la **décrit**, sans jamais la créer.

La connexion se règle dans `BACKEND/.env`, ligne `DATABASE_URL` :

```
mysql+pymysql://utilisateur:motdepasse@127.0.0.1:3307/nom_base?charset=utf8mb4
```

Changer de SGBD (PostgreSQL, SQL Server, Oracle) ne demanderait que cette ligne et le pilote
Python correspondant.

**Vérifier la connexion** : l'API lancée, ouvrir http://localhost:5000/health. Tout va bien si la
réponse contient `"status": "ok"` et `"reachable": true`. Sinon (`"degraded"`), le détail de
l'erreur s'affiche dans le terminal de l'API.

## Exporter et restaurer la base (`mysqldump`)

Un export est un fichier `.sql` qui recrée la base telle qu'elle est (schéma, vues, données, et
la table `migration_appliquee`). Il sert à garder une copie avant une manipulation risquée ou à
transmettre la base en fin de projet.

Exporter (la base tourne, depuis la racine du projet) :

```bash
docker compose exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysqldump -uroot --single-transaction --routines --triggers --no-tablespaces --default-character-set=utf8mb4 "$MYSQL_DATABASE"' > sauvegarde-enroute-$(date +%F).sql
```

`-T` évite les fins de ligne Windows ; `--single-transaction` donne une copie cohérente sans
bloquer l'API. Schéma seul : ajouter `--no-data`.

Restaurer dans une base vide :

```bash
docker compose down -v && docker compose up -d db   # EFFACE la base actuelle
docker compose exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot --default-character-set=utf8mb4 "$MYSQL_DATABASE"' < sauvegarde-enroute-AAAA-MM-JJ.sql
```

Testé le 12/11/2026. À savoir : l'export local contient les **comptes de test au mot de passe
public** (ne jamais le charger sur un serveur accessible) ; un export de vraies données contient
des **données personnelles** (le ranger chiffré, hors du dépôt, et le supprimer quand il ne sert
plus) ; les vues sont créées au nom de `root@localhost`, qui doit exister sur le serveur qui
restaure.

## Ce que l'équipe BD a livré

| Livré | Fichier | Issue |
|---|---|---|
| Schéma v2 validé, MySQL 8.4 ; photo du chauffeur en `MEDIUMBLOB` | `sql/schema-mvp.sql` | #20, #22 |
| Colonne `version_session` sur `utilisateur` | `001` | #21 |
| Demandes de suppression de compte | `002` | #32 |
| Vues des statistiques, par jour en heure de Guyane | `003` à `006` | #23 |
| Vue des chauffeurs en ligne et tri par distance | `007` | #24 |
| Migrations sans effacer la base (`migration_appliquee`, `sql/migrer.sh`, service `db-migrate`) | `sql/migrer.sh`, `compose.yaml` | #82 |
| Export et restauration par `mysqldump` | ce guide | #26 |
| Langues de l'application (`fr`, `gcr`, `ht`, `pt-BR`, `en`) | `009` | #48, #49 |
| Les 22 communes de Guyane, zone du pilote | `010` | #52 |
| Offres d'emploi et traductions ; 15 offres fictives | `011`, `014` | #48 |
| Services d'aide ; 16 services fictifs | `012`, `015` | #49 |
| Fiches pratiques ; 8 fiches | `013`, `016` | #49 |
| Questionnaire, plan d'action et ses étapes | `017` | #50 |
| Horaires autorisés, en heure de Cayenne | `018` | #51 |
| Repère, passagers, bagages | `019` | #53 |
| États « chauffeur arrivé », « passager absent », paiement échoué | `020` à `022` | #54 |
| Journal des étapes d'une course, avec leur auteur | `023` | #55 |
| Pièces et zones du chauffeur | `024`, `026` | #56 |
| Compte supprimé et anonymisé | `025` | #32 |
| « Être rappelé » et « Signaler un problème » | `027` | #57 |

Les numéros renvoient aux fichiers de `sql/migrations/`. Chacun explique en tête comment s'en
servir depuis l'API.

## Ce qui reste à faire

1. **Les tables des bons solidaires**, dès que la cliente aura dit comment marche un bon (point de
   départ : `sql/schema-hors-scope.sql`, #25). Après la soutenance (P2).
2. **Votre partie du rapport de gestion et de la soutenance** : le temps passé par chacun, et qui
   présente quoi sur la base.
3. En continu : les **données de référence**, toujours fictives pour les tests (RGPD : faux noms,
   faux téléphones, fausses adresses).

## Demander un changement de schéma

Les développeurs ouvrent une **issue GitHub** avec l'étiquette `bd` :

- le besoin en une phrase, et la fonctionnalité concernée (cas d'utilisation, route) ;
- la table ou la colonne proposée (nom, type, contraintes), comme simple suggestion ;
- la date à laquelle l'API en a besoin.

Vous répondez dans l'issue, puis vous livrez la migration par une pull request qui cite l'issue.
Un développeur la relit pour vérifier que l'API pourra s'en servir.

## Ce qui nous aide

- **Des noms en minuscules avec des underscores** (`bon_solidaire`, `date_reservation`).
- **Des contraintes en base** (clés étrangères, `NOT NULL`, `CHECK`, unicité) : elles protègent
  les données même si l'API a un bug.
- **La traçabilité des trajets financés** (P2) : qui a financé quel trajet, avec quel bon, quand.
- **Garder les données de test séparées du schéma** (`sql/demo-data.sql`) : un environnement
  hébergé ne charge que le schéma et les données de référence (audit de sécurité du 02/11/2026).
