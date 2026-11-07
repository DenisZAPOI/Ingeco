"""
The test database: a MySQL 8.4 built from the DB team's own scripts.

Built once per test run, the same way the local container does it
(sql/charger-base.sh): sql/schema-mvp.sql, then every file of sql/migrations/
in order. NOT sql/demo-data.sql: each test writes the rows it needs.

Locally: `docker compose --profile test up -d db-test` (port 3308). In the CI:
a MySQL service of the workflow. Never point TEST_DATABASE_URL at a database
whose content matters: it is dropped and created again at every run.
"""

from pathlib import Path

import pymysql
from pymysql.constants import CLIENT
from sqlalchemy import Engine, text
from sqlalchemy.engine import make_url

SQL_DIR = Path(__file__).resolve().parents[2] / "sql"

# Rows written by the API, children first (foreign keys). The reference data
# (role, commune, tarif) comes from the schema and is never touched.
DATA_TABLES = ("evaluation", "course", "demande_suppression", "vehicule", "chauffeur", "usager", "utilisateur")

UNREACHABLE = (
    "The test database does not answer at {where}.\n"
    "Start it with: docker compose --profile test up -d db-test\n"
    "(or set TEST_DATABASE_URL to a MySQL 8.4 that can be wiped)."
)


def schema_files() -> list[Path]:
    """The scripts of the DB team, in the order they load them."""
    return [SQL_DIR / "schema-mvp.sql", *sorted((SQL_DIR / "migrations").glob("*.sql"))]


def create(database_url: str) -> None:
    """Drops the test database, creates it again and loads the schema into it."""
    url = make_url(database_url)
    try:
        connection = pymysql.connect(
            host=url.host,
            port=url.port or 3306,
            user=url.username,
            password=url.password or "",
            charset="utf8mb4",
            client_flag=CLIENT.MULTI_STATEMENTS,
            autocommit=True,
        )
    except pymysql.err.OperationalError as error:
        raise RuntimeError(UNREACHABLE.format(where=f"{url.host}:{url.port}")) from error

    name = url.database
    with connection, connection.cursor() as cursor:
        cursor.execute(f"DROP DATABASE IF EXISTS `{name}`")
        cursor.execute(f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE `{name}`")
        for script in schema_files():
            cursor.execute(script.read_text(encoding="utf-8"))
            # A script holds many statements: read every result, or the next
            # script would be refused (commands out of sync).
            while cursor.nextset():
                pass


def empty(engine: Engine) -> None:
    """Removes the rows written by a test; keeps the reference data."""
    with engine.begin() as connection:
        for table in DATA_TABLES:
            connection.execute(text(f"DELETE FROM {table}"))
