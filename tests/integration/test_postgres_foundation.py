"""M03 acceptance against PostgreSQL, never SQLite or a mocked query executor."""

from uuid import UUID, uuid4

import psycopg
import pytest
from sqlalchemy.exc import DBAPIError

from access.db import create_pool, tenant_connection
from ledger.db.migrate import bootstrap_roles, downgrade, revision, upgrade

pytestmark = pytest.mark.integration
TENANT_A = UUID("11111111-1111-4111-8111-111111111111")
TENANT_B = UUID("22222222-2222-4222-8222-222222222222")
BASKET_ID = UUID("33333333-3333-4333-8333-333333333333")


def test_migration_from_empty_database_and_repeat_upgrade(database):
    bootstrap_roles(database.admin_dsn)
    assert revision(database.admin_dsn) is None
    upgrade(database.admin_dsn)
    assert revision(database.admin_dsn) == "0001_foundation"
    upgrade(database.admin_dsn)
    assert revision(database.admin_dsn) == "0001_foundation"
    downgrade(database.admin_dsn)
    assert revision(database.admin_dsn) is None
    upgrade(database.admin_dsn)
    assert revision(database.admin_dsn) == "0001_foundation"


def test_failed_migration_rolls_back_prior_ddl_and_can_recover(database):
    with database.admin() as connection:
        connection.execute("CREATE SCHEMA app")
        connection.execute("CREATE TABLE app.baskets (marker integer)")
        connection.execute("INSERT INTO app.baskets VALUES (7)")
    with pytest.raises(DBAPIError):
        upgrade(database.admin_dsn)
    with database.admin() as connection:
        assert connection.execute("SELECT to_regnamespace('catalog')").fetchone() == (None,)
        assert connection.execute("SELECT marker FROM app.baskets").fetchall() == [(7,)]
        assert revision(database.admin_dsn) is None
        connection.execute("DROP SCHEMA app CASCADE")
    upgrade(database.admin_dsn)
    assert revision(database.admin_dsn) == "0001_foundation"


def test_runtime_login_is_restricted_and_tables_force_rls(migrated):
    with migrated.runtime() as connection:
        assert connection.execute("SELECT session_user, current_user").fetchone() == (
            migrated.runtime_role,
            migrated.runtime_role,
        )
        assert connection.execute(
            "SELECT rolsuper, rolcreatedb, rolcreaterole, rolbypassrls "
            "FROM pg_roles WHERE rolname = current_user"
        ).fetchone() == (False, False, False, False)
    with migrated.admin() as connection:
        tables = connection.execute(
            "SELECT c.relname, pg_get_userbyid(c.relowner), "
            "c.relrowsecurity, c.relforcerowsecurity "
            "FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
            "WHERE n.nspname='app' AND c.relkind='r' ORDER BY c.relname"
        ).fetchall()
        assert {row[0] for row in tables} == {"tenants", "memberships", "baskets", "audit_log"}
        assert all(row[1:] == ("fi_owner", True, True) for row in tables)


@pytest.mark.parametrize("table", ["tenants", "memberships", "baskets", "audit_log"])
def test_absent_tenant_context_exposes_no_tenant_rows(migrated, table):
    with migrated.runtime() as connection:
        rows = connection.execute(
            psycopg.sql.SQL("SELECT tenant_id FROM app.{}").format(psycopg.sql.Identifier(table))
        ).fetchall()
        assert rows == []


def test_absent_context_cannot_insert_tenant_rows(migrated):
    with migrated.runtime() as connection:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            connection.execute(
                "INSERT INTO app.baskets (tenant_id, basket_id, name) VALUES (%s, %s, 'denied')",
                (TENANT_A, uuid4()),
            )


def test_context_limits_reads_updates_deletes_and_insert_checks(migrated):
    with create_pool(migrated.runtime_dsn, min_size=1, max_size=1) as pool:
        with tenant_connection(pool, TENANT_A) as connection:
            for table in ("tenants", "memberships", "baskets", "audit_log"):
                rows = connection.execute(
                    psycopg.sql.SQL("SELECT tenant_id FROM app.{}").format(
                        psycopg.sql.Identifier(table)
                    )
                ).fetchall()
                assert rows and all(row == (TENANT_A,) for row in rows)
            assert (
                connection.execute(
                    "UPDATE app.baskets SET name='hidden edit' WHERE tenant_id=%s", (TENANT_B,)
                ).rowcount
                == 0
            )
            assert (
                connection.execute(
                    "DELETE FROM app.baskets WHERE tenant_id=%s", (TENANT_B,)
                ).rowcount
                == 0
            )
            connection.execute(
                "UPDATE app.baskets SET name='Allowed update' WHERE tenant_id=%s", (TENANT_A,)
            )
            connection.execute(
                "INSERT INTO app.baskets (tenant_id, basket_id, name) VALUES (%s, %s, 'allowed')",
                (TENANT_A, uuid4()),
            )
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with tenant_connection(pool, TENANT_A) as connection:
                connection.execute(
                    "INSERT INTO app.baskets (tenant_id, basket_id, name) "
                    "VALUES (%s, %s, 'cross tenant')",
                    (TENANT_B, uuid4()),
                )
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with tenant_connection(pool, TENANT_A) as connection:
                connection.execute(
                    "UPDATE app.baskets SET tenant_id=%s WHERE tenant_id=%s",
                    (TENANT_B, TENANT_A),
                )
        with tenant_connection(pool, TENANT_B) as connection:
            assert connection.execute("SELECT name FROM app.baskets").fetchall() == [("Tenant B",)]


def test_single_connection_pool_does_not_leak_context_after_commit_or_exception(migrated):
    with create_pool(migrated.runtime_dsn, min_size=1, max_size=1) as pool:
        with tenant_connection(pool, TENANT_A) as connection:
            backend = connection.execute("SELECT pg_backend_pid()").fetchone()[0]
            assert connection.execute("SELECT tenant_id FROM app.tenants").fetchall() == [
                (TENANT_A,)
            ]
        with pool.connection() as connection:
            assert connection.execute("SELECT pg_backend_pid()").fetchone()[0] == backend
            assert connection.execute("SELECT tenant_id FROM app.tenants").fetchall() == []
        with pytest.raises(RuntimeError, match="rollback marker"):
            with tenant_connection(pool, TENANT_B) as connection:
                connection.execute(
                    "INSERT INTO app.baskets (tenant_id, basket_id, name) "
                    "VALUES (%s, %s, 'rollback')",
                    (TENANT_B, uuid4()),
                )
                raise RuntimeError("rollback marker")
        with pool.connection() as connection:
            assert connection.execute("SELECT pg_backend_pid()").fetchone()[0] == backend
            assert connection.execute("SELECT tenant_id FROM app.tenants").fetchall() == []
        with tenant_connection(pool, TENANT_B) as connection:
            assert connection.execute("SELECT name FROM app.baskets").fetchall() == [("Tenant B",)]


def test_stale_session_context_is_cleared_before_and_after_request(migrated):
    with create_pool(migrated.runtime_dsn, min_size=1, max_size=1) as pool:
        with pool.connection() as connection:
            connection.execute("SELECT set_config('app.tenant_id', %s, false)", (str(TENANT_B),))
        with tenant_connection(pool, TENANT_A) as connection:
            assert connection.execute("SELECT tenant_id FROM app.tenants").fetchall() == [
                (TENANT_A,)
            ]
        with pool.connection() as connection:
            assert connection.execute("SELECT tenant_id FROM app.tenants").fetchall() == []


@pytest.mark.parametrize(
    "statement",
    [
        "UPDATE app.audit_log SET action='tamper'",
        "DELETE FROM app.audit_log",
        "TRUNCATE app.audit_log",
        "UPDATE app.tenants SET name='tamper'",
        "DELETE FROM app.memberships",
        "SET ROLE fi_owner",
        "SET ROLE fi_publisher",
        "CREATE TABLE app.forbidden (value integer)",
        "ALTER TABLE app.baskets DISABLE ROW LEVEL SECURITY",
        "TRUNCATE app.baskets",
    ],
)
def test_runtime_cannot_mutate_audit_identity_or_assume_privileged_roles(migrated, statement):
    with create_pool(migrated.runtime_dsn, min_size=1, max_size=1) as pool:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with tenant_connection(pool, TENANT_A) as connection:
                connection.execute(statement)


def test_runtime_audit_insert_is_tenant_scoped(migrated):
    event_id = uuid4()
    with create_pool(migrated.runtime_dsn, min_size=1, max_size=1) as pool:
        with tenant_connection(pool, TENANT_A) as connection:
            connection.execute(
                "INSERT INTO app.audit_log (tenant_id, event_id, actor, action) "
                "VALUES (%s, %s, 'analyst', 'query')",
                (TENANT_A, event_id),
            )
            assert connection.execute(
                "SELECT action FROM app.audit_log WHERE event_id=%s", (event_id,)
            ).fetchone() == ("query",)
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with tenant_connection(pool, TENANT_A) as connection:
                connection.execute(
                    "INSERT INTO app.audit_log (tenant_id, event_id, actor, action) "
                    "VALUES (%s, %s, 'analyst', 'query')",
                    (TENANT_B, uuid4()),
                )


def test_catalog_grants_and_commit_pointer_references(migrated):
    version = "a" * 64
    with migrated.runtime() as connection:
        assert (
            connection.execute("SELECT data_version FROM catalog.dataset_versions").fetchall() == []
        )
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            connection.execute(
                "INSERT INTO catalog.dataset_versions "
                "(data_version, manifest, schema_version, code_version) "
                "VALUES (%s, '{}', '1', 'code')",
                (version,),
            )
    with migrated.publisher() as connection:
        connection.execute(
            "INSERT INTO catalog.dataset_versions "
            "(data_version, manifest, schema_version, code_version) VALUES (%s, '{}', '1', 'code')",
            (version,),
        )
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            connection.execute(
                "INSERT INTO catalog.current_dataset (data_version) VALUES (%s)", (version,)
            )
        connection.execute(
            "INSERT INTO catalog.catalog_commits (data_version, run_id) VALUES (%s, %s)",
            (version, uuid4()),
        )
        connection.execute(
            "INSERT INTO catalog.current_dataset (data_version) VALUES (%s)", (version,)
        )
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            connection.execute("DELETE FROM catalog.dataset_versions")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            connection.execute("SELECT * FROM app.tenants")
    with migrated.runtime() as connection:
        assert connection.execute(
            "SELECT data_version FROM catalog.current_dataset"
        ).fetchone() == (version,)


def test_invalid_tenant_identifier_is_rejected_before_query(migrated):
    with create_pool(migrated.runtime_dsn, min_size=1, max_size=1) as pool:
        with pytest.raises((TypeError, ValueError)):
            with tenant_connection(pool, "not-a-uuid"):
                pytest.fail("Untrusted tenant identifiers cannot enter a request transaction.")


def test_existing_owner_default_grants_do_not_broaden_runtime_permissions(database):
    with database.admin() as connection:
        connection.execute(
            "ALTER DEFAULT PRIVILEGES FOR ROLE fi_owner GRANT ALL ON TABLES TO PUBLIC"
        )
        connection.execute(
            "ALTER DEFAULT PRIVILEGES FOR ROLE fi_owner GRANT ALL ON SEQUENCES TO PUBLIC"
        )
    upgrade(database.admin_dsn)
    with database.runtime() as connection:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            connection.execute("UPDATE app.audit_log SET action='tamper'")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            connection.execute("DELETE FROM catalog.dataset_versions")


def test_pool_rejects_superuser_connections(migrated):
    with pytest.raises(PermissionError) as error:
        with create_pool(migrated.admin_dsn, min_size=1, max_size=1):
            pass
    assert type(error.value).__name__ == "UnsafeDatabaseRoleError"


def test_runtime_role_elevation_is_rejected_between_requests(migrated):
    assert migrated.runtime_role.startswith("fi_test_runtime_")
    with create_pool(migrated.runtime_dsn, min_size=1, max_size=1) as pool:
        with tenant_connection(pool, TENANT_A) as connection:
            assert connection.execute("SELECT tenant_id FROM app.tenants").fetchall() == [
                (TENANT_A,)
            ]
        try:
            with migrated.admin() as connection:
                connection.execute(
                    psycopg.sql.SQL("ALTER ROLE {} BYPASSRLS").format(
                        psycopg.sql.Identifier(migrated.runtime_role)
                    )
                )
            with pytest.raises(PermissionError) as error:
                with tenant_connection(pool, TENANT_A):
                    pytest.fail("An elevated database role cannot enter a tenant request.")
            assert type(error.value).__name__ == "UnsafeDatabaseRoleError"
        finally:
            with migrated.admin() as connection:
                connection.execute(
                    psycopg.sql.SQL("ALTER ROLE {} NOBYPASSRLS").format(
                        psycopg.sql.Identifier(migrated.runtime_role)
                    )
                )


def test_catalog_parent_must_already_be_committed(migrated):
    parent, child = "a" * 64, "b" * 64
    with migrated.publisher() as connection:
        for version in (parent, child):
            connection.execute(
                "INSERT INTO catalog.dataset_versions "
                "(data_version, manifest, schema_version, code_version) "
                "VALUES (%s, '{}', '1', 'code')",
                (version,),
            )
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            connection.execute(
                "INSERT INTO catalog.catalog_commits (data_version, parent_version, run_id) "
                "VALUES (%s, %s, %s)",
                (child, parent, uuid4()),
            )
        connection.execute(
            "INSERT INTO catalog.catalog_commits (data_version, run_id) VALUES (%s, %s)",
            (parent, uuid4()),
        )
        connection.execute(
            "INSERT INTO catalog.catalog_commits (data_version, parent_version, run_id) "
            "VALUES (%s, %s, %s)",
            (child, parent, uuid4()),
        )
