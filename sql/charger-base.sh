#!/bin/bash
# Création de la base locale, lancée par le conteneur MySQL au premier
# démarrage seulement (base vide). Voir compose.yaml.
#
# Ordre : le schéma, puis toutes les migrations par ordre de numéro, puis les
# données de test en dernier (elles peuvent remplir des colonnes ajoutées
# par les migrations). Une nouvelle migration est prise en compte sans
# toucher à compose.yaml.
#
# Le client mysql est appelé directement, plutôt que la fonction
# docker_process_sql de l'image : celle-ci n'existe que si le fichier est
# « sourcé », or un fichier monté depuis Windows paraît exécutable, et
# l'image l'exécute alors à part. Une erreur SQL arrête la création.

set -e

for fichier in /sql/schema-mvp.sql /sql/migrations/*.sql /sql/demo-data.sql; do
    [ -f "$fichier" ] || continue
    echo "charger-base : $fichier"
    MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql --protocol=socket -uroot \
        --socket="${SOCKET:-/var/run/mysqld/mysqld.sock}" \
        --default-character-set=utf8mb4 "$MYSQL_DATABASE" < "$fichier"
done
