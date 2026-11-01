"""Disposable PostgreSQL resources; never mutate a user application database."""

import os
from collections.abc import Iterator
from dataclasses import dataclass
from uuid import UUID, uuid4

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from ledger.db.migrate import bootstrap_roles, upgrade

TENANT_A = UUID("11111111-1111-4111-8111-111111111111")
TENANT_B = UUID("22222222-2222-4222-8222-222222222222")
BASKET_ID = UUID("33333333-3333-4333-8333-333333333333")


@dataclass(frozen=True, repr=False)
class TestDatabase:
    admin_dsn: str
    runtime_dsn: str
    publisher_dsn: str
    runtime_role: str

    def admin(self) -> psycopg.Connection:
        return psycopg.connect(self.admin_dsn, autocommit=True)

    def runtime(self) -> psycopg.Connection:
        return psycopg.connect(self.runtime_dsn, autocommit=True)

    def publisher(self) -> psycopg.Connection:
        return psycopg.connect(self.publisher_dsn, autocommit=True)


@pytest.fixture
def database(monkeypatch) -> Iterator[TestDatabase]:
    supplied = os.environ.get("FI_TEST_ADMIN_DSN")
    if not supplied:
        pytest.fail("Integration tests require FI_TEST_ADMIN_DSN for a disposable local server.")
    options = conninfo_to_dict(supplied)
    host = options.get("host", "")
    if not (host in {"127.0.0.1", "::1", "localhost"} or host.startswith("/")):
        pytest.fail("FI_TEST_ADMIN_DSN must name an explicit loopback host or Unix socket.")
    if options.get("service") or options.get("hostaddr", "127.0.0.1") not in {
        "127.0.0.1",
        "::1",
    }:
        pytest.fail("Integration test DSNs cannot redirect to a service or remote host address.")
    # Libpq otherwise consults ambient settings even with an explicit host.
    # Remove routing/service settings only for this fixture's lifetime.
    for name in (
        "PGHOST",
        "PGHOSTADDR",
        "PGPORT",
        "PGDATABASE",
        "PGUSER",
        "PGSERVICE",
        "PGSERVICEFILE",
        "PGOPTIONS",
    ):
        monkeypatch.delenv(name, raising=False)
    routing = {"host": "127.0.0.1" if host == "localhost" else host}
    if host.startswith("/"):
        if options.get("hostaddr"):
            pytest.fail("Unix-socket test DSNs cannot also specify a TCP host address.")
    else:
        routing["hostaddr"] = routing["host"]
    control_dsn = make_conninfo(supplied, **routing)
    token = uuid4().hex
    name = f"fi_test_{token}"
    runtime_role, publisher_role = f"fi_test_runtime_{token}", f"fi_test_pub_{token}"
    created_database = False
    created_roles = []
    connection_options = {**routing, "port": options.get("port", "5432"), "dbname": name}
    admin_dsn = make_conninfo(control_dsn, dbname=name)
    # Tests require a local trust-authenticated server. No password is persisted
    # in a repository, fixture, log, or generated configuration.
    with psycopg.connect(control_dsn, autocommit=True) as control:
        try:
            control.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
            created_database = True
            bootstrap_roles(admin_dsn)
            for role, group in ((runtime_role, "fi_runtime"), (publisher_role, "fi_publisher")):
                control.execute(
                    sql.SQL(
                        "CREATE ROLE {} LOGIN INHERIT NOSUPERUSER NOCREATEDB "
                        "NOCREATEROLE NOREPLICATION NOBYPASSRLS"
                    ).format(sql.Identifier(role))
                )
                created_roles.append(role)
                control.execute(
                    sql.SQL("GRANT {} TO {}").format(sql.Identifier(group), sql.Identifier(role))
                )
            yield TestDatabase(
                admin_dsn=admin_dsn,
                runtime_dsn=make_conninfo("", user=runtime_role, **connection_options),
                publisher_dsn=make_conninfo("", user=publisher_role, **connection_options),
                runtime_role=runtime_role,
            )
        finally:
            # Only names allocated above are eligible for cleanup.
            assert name == f"fi_test_{token}"
            if created_database:
                control.execute(
                    sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name))
                )
            for role in reversed(created_roles):
                control.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(role)))


@pytest.fixture
def migrated(database: TestDatabase) -> TestDatabase:
    upgrade(database.admin_dsn)
    with database.admin() as connection:
        for tenant, name in ((TENANT_A, "Tenant A"), (TENANT_B, "Tenant B")):
            connection.execute(
                "INSERT INTO app.tenants (tenant_id, name) VALUES (%s, %s)", (tenant, name)
            )
            connection.execute(
                "INSERT INTO app.memberships (tenant_id, subject, role) VALUES (%s, %s, 'owner')",
                (tenant, f"owner-{name}"),
            )
            connection.execute(
                "INSERT INTO app.baskets (tenant_id, basket_id, name, fund_ids) "
                "VALUES (%s, %s, %s, %s)",
                (tenant, BASKET_ID, name, ["fund-a"]),
            )
            connection.execute(
                "INSERT INTO app.audit_log (tenant_id, event_id, actor, action) "
                "VALUES (%s, %s, 'operator', 'seed')",
                (tenant, uuid4()),
            )
    return database
