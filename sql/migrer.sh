#!/bin/bash
# Applique à une base DÉJÀ CRÉÉE les migrations de sql/migrations/ qu'elle
# n'a pas encore reçues, sans rien effacer (issue #82).
#
# La table migration_appliquee garde le numéro de chaque migration
# appliquée. Le script lit sql/migrations/ par ordre de numéro, saute
# celles qui y sont déjà, applique les autres une par une et note chacune
# APRÈS son succès. Une erreur SQL arrête tout : la migration en échec
# n'est pas notée, et le script la retentera au prochain lancement.
# Attention : MySQL valide chaque CREATE ou ALTER aussitôt (pas de retour
# en arrière sur le schéma). Une migration de plusieurs instructions qui
# échoue au milieu peut donc laisser les premières appliquées : lire
# l'erreur, réparer à la main (retour arrière en tête du fichier), puis
# relancer.
#
# Lancé :
#   - à chaque démarrage, par le service db-migrate de compose.yaml, qui
#     attend que la base soit prête, applique ce qui manque puis s'arrête ;
#     l'API attend qu'il ait fini ;
#   - à la création de la base, par charger-base.sh (BASE_NEUVE=1).
#
# Une base créée avant ce script (001 à 008 déjà chargées par
# charger-base.sh, mais sans la table) : le script crée la table et y note
# 001 à 008 sans les rejouer, puis applique celles qui suivent.
#
# Réglages (variables d'environnement) :
#   MYSQL_DATABASE       la base à migrer
#   MYSQL_ROOT_PASSWORD  mot de passe de root (les migrations changent le schéma)
#   MYSQL_HOST           serveur MySQL ; vide = le socket local (charger-base.sh)
#   MYSQL_PORT           3306 par défaut
#   SQL_DIR              dossier sql/ ; /sql par défaut (montage de compose.yaml)
#   BASE_NEUVE           1 = la base vient d'être créée : rien n'est déjà appliqué

set -euo pipefail

SQL_DIR="${SQL_DIR:-/sql}"
# Dernière migration chargée par charger-base.sh avant ce script
DERNIERE_AVANT_SUIVI=8

connexion=(--default-character-set=utf8mb4 -uroot)
if [ -n "${MYSQL_HOST:-}" ]; then
    connexion+=(--protocol=tcp -h "$MYSQL_HOST" -P "${MYSQL_PORT:-3306}")
else
    connexion+=(--protocol=socket --socket="${SOCKET:-/var/run/mysqld/mysqld.sock}")
fi
export MYSQL_PWD="$MYSQL_ROOT_PASSWORD"

sql() { mysql "${connexion[@]}" "$MYSQL_DATABASE" "$@"; }
# Une seule valeur, sans en-tête
valeur() { sql -N -B -e "$1"; }

table_existe() {
    valeur "SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_name = '$1'"
}

if [ "$(table_existe migration_appliquee)" = 0 ]; then
    base_deja_creee=0
    if [ "${BASE_NEUVE:-0}" != 1 ] && [ "$(table_existe utilisateur)" = 1 ]; then
        base_deja_creee=1
    fi

    sql <<'SQL'
-- Migrations reçues par cette base (issue #82). Écrite par sql/migrer.sh
-- seulement, jamais par l'API.
CREATE TABLE migration_appliquee (
    numero        CHAR(3)      PRIMARY KEY,
    fichier       VARCHAR(255) NOT NULL,
    -- UTC, comme toutes les dates du schéma
    appliquee_le  DATETIME     NOT NULL,
    CONSTRAINT chk_migration_appliquee_numero CHECK (numero REGEXP '^[0-9]{3}$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
SQL
    echo "migrer : table migration_appliquee créée"

    if [ "$base_deja_creee" = 1 ]; then
        for fichier in "$SQL_DIR"/migrations/*.sql; do
            nom=$(basename "$fichier")
            numero=${nom:0:3}
            if [ "$((10#$numero))" -le "$DERNIERE_AVANT_SUIVI" ]; then
                valeur "INSERT INTO migration_appliquee (numero, fichier, appliquee_le)
                        VALUES ('$numero', '$nom', UTC_TIMESTAMP())" > /dev/null
                echo "migrer : $nom déjà dans la base (créée avant le suivi), notée sans la rejouer"
            fi
        done
    fi
fi

appliquees=0
for fichier in "$SQL_DIR"/migrations/*.sql; do
    [ -f "$fichier" ] || continue
    nom=$(basename "$fichier")
    numero=${nom:0:3}
    if ! [[ "$numero" =~ ^[0-9]{3}$ ]] || [ "${nom:3:1}" != "_" ]; then
        echo "migrer : nom refusé, attendu NNN_description.sql : $nom" >&2
        exit 1
    fi
    if [ "$(valeur "SELECT COUNT(*) FROM migration_appliquee WHERE numero = '$numero'")" != 0 ]; then
        continue
    fi

    echo "migrer : $nom"
    if ! sql < "$fichier"; then
        echo "migrer : ÉCHEC de $nom, non notée ; les suivantes ne sont pas appliquées" >&2
        exit 1
    fi
    valeur "INSERT INTO migration_appliquee (numero, fichier, appliquee_le)
            VALUES ('$numero', '$nom', UTC_TIMESTAMP())" > /dev/null
    appliquees=$((appliquees + 1))
done

echo "migrer : $appliquees migration(s) appliquée(s), base à jour"
