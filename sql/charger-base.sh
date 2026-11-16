#!/bin/bash
# Création de la base locale, lancée par le conteneur MySQL au premier
# démarrage seulement (base vide). Voir compose.yaml.
#
# Ordre : le schéma, puis toutes les migrations par ordre de numéro, puis les
# données de test en dernier (elles peuvent remplir des colonnes ajoutées
# par les migrations). Une nouvelle migration est prise en compte sans
# toucher à compose.yaml.
#
# Les migrations passent par migrer.sh, qui note chacune dans la table
# migration_appliquee : aux démarrages suivants, le service db-migrate de
# compose.yaml n'applique que celles qui manquent, sans effacer la base
# (issue #82).
#
# Le client mysql est appelé directement, plutôt que la fonction
# docker_process_sql de l'image : celle-ci n'existe que si le fichier est
# « sourcé », or un fichier monté depuis Windows paraît exécutable, et
# l'image l'exécute alors à part. Une erreur SQL arrête la création.

set -e

charger() {
    echo "charger-base : $1"
    MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql --protocol=socket -uroot \
        --socket="${SOCKET:-/var/run/mysqld/mysqld.sock}" \
        --default-character-set=utf8mb4 "$MYSQL_DATABASE" < "$1"
}

charger /sql/schema-mvp.sql
# bash explicite : le fichier monté n'est pas forcément exécutable
BASE_NEUVE=1 SQL_DIR=/sql bash /sql/migrer.sh
charger /sql/demo-data.sql
