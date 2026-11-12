"""
The test database: a MySQL 8.4 built from the DB team's own scripts.

Built once per test run, the same way the local container does it
(sql/charger-base.sh): sql/schema-mvp.sql, then every file of sql/migrations/
in order. Before each test, sql/demo-data.sql is loaded again: it erases the
rows of the previous test itself, so every test starts from the demo accounts
and rides, the same ones as the local database.

Locally: `docker compose --profile test up -d db-test` (port 3308). In the CI:
a MySQL service of the workflow. Never point TEST_DATABASE_URL at a database
whose content matters: it is dropped and created again at every run.
"""

from pathlib import Path

import pymysql
from pymysql.constants import CLIENT
from sqlalchemy.engine import make_url

SQL_DIR = Path(__file__).resolve().parents[2] / "sql"

UNREACHABLE = (
    "The test database does not answer at {where}.\n"
    "Start it with: docker compose --profile test up -d db-test\n"
    "(or set TEST_DATABASE_URL to a MySQL 8.4 that can be wiped)."
)


def schema_files() -> list[Path]:
    """The scripts of the DB team, in the order they load them."""
    return [SQL_DIR / "schema-mvp.sql", *sorted((SQL_DIR / "migrations").glob("*.sql"))]


DEMO_DATA = SQL_DIR / "demo-data.sql"


def create(database_url: str) -> None:
    """Drops the test database, creates it again and loads the schema into it."""
    url = make_url(database_url)
    name = url.database
    with _connect(database_url) as connection, connection.cursor() as cursor:
        cursor.execute(f"DROP DATABASE IF EXISTS `{name}`")
        cursor.execute(f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE `{name}`")
        for script in schema_files():
            _run_script(cursor, script)


def reset_demo_data(database_url: str) -> None:
    """Loads sql/demo-data.sql again: it erases the rows of the previous test first.

    The same script as the local "reset the demo" command (README), so the
    list of tables to erase lives in one place.
    """
    with _connect(database_url, database=make_url(database_url).database) as connection:
        with connection.cursor() as cursor:
            _run_script(cursor, DEMO_DATA)


def _connect(database_url: str, database: str | None = None) -> pymysql.Connection:
    url = make_url(database_url)
    try:
        return pymysql.connect(
            host=url.host,
            port=url.port or 3306,
            user=url.username,
            password=url.password or "",
            database=database,
            charset="utf8mb4",
            client_flag=CLIENT.MULTI_STATEMENTS,
            autocommit=True,
        )
    except pymysql.err.OperationalError as error:
        raise RuntimeError(UNREACHABLE.format(where=f"{url.host}:{url.port}")) from error


def _run_script(cursor, script: Path) -> None:
    cursor.execute(script.read_text(encoding="utf-8"))
    # A script holds many statements: read every result, or the next
    # script would be refused (commands out of sync).
    while cursor.nextset():
        pass
