"""The ORM models follow the DB team's tables, column for column.

If the DB team adds, renames or drops a column in a migration, these tests say
which model to update (app/models/). The models never change the schema.
"""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.models import Commune, Role, TariffRow
from app.models.types import UtcDateTime
from app.services.account_rules import ROLES
from app.utils.database import Base

# Columns computed by MySQL (GENERATED ALWAYS): never written by the API.
COMPUTED_COLUMNS = {("tarif", "tarif_actif"), ("demande_suppression", "demande_en_cours")}


@pytest.mark.parametrize("table", sorted(Base.metadata.tables.values(), key=lambda table: table.name), ids=str)
def test_a_model_has_exactly_the_columns_of_its_table(test_database, table):
    in_database = {
        column["name"]: column for column in inspect(test_database).get_columns(table.name)
        if (table.name, column["name"]) not in COMPUTED_COLUMNS
    }

    assert set(table.columns.keys()) == set(in_database)


@pytest.mark.parametrize("table", sorted(Base.metadata.tables.values(), key=lambda table: table.name), ids=str)
def test_a_model_column_is_optional_only_where_the_table_allows_null(test_database, table):
    in_database = {column["name"]: column["nullable"] for column in inspect(test_database).get_columns(table.name)}

    for column in table.columns:
        if not column.primary_key:
            assert column.nullable == in_database[column.name], column.name


def test_every_table_of_the_schema_has_a_model(test_database):
    tables = set(inspect(test_database).get_table_names())

    assert tables == set(Base.metadata.tables)


def test_the_reference_data_comes_from_the_schema(test_database):
    with Session(test_database) as session:
        assert session.scalars(select(Commune.name).order_by(Commune.name)).all() == [
            "Cayenne",
            "Matoury",
            "Rémire-Montjoly",
        ]
        assert session.scalars(select(TariffRow).where(TariffRow.is_active.is_(True))).one().id == 1


@pytest.mark.xfail(strict=True, reason="role 'partner' asked to the DB team (issue #44, migration 008)")
def test_every_role_of_the_api_exists_in_the_database(test_database):
    with Session(test_database) as session:
        assert set(ROLES) <= set(session.scalars(select(Role.code)))


def test_a_date_is_stored_in_utc_and_read_back_with_its_zone():
    column = UtcDateTime()
    guyana = timezone(timedelta(hours=-3))

    stored = column.process_bind_param(datetime(2026, 11, 7, 22, 0, tzinfo=guyana), None)
    read = column.process_result_value(stored, None)

    assert stored == datetime(2026, 11, 8, 1, 0)
    assert read == datetime(2026, 11, 8, 1, 0, tzinfo=timezone.utc)


def test_a_date_without_zone_is_refused():
    with pytest.raises(ValueError):
        UtcDateTime().process_bind_param(datetime(2026, 11, 7, 22, 0), None)
