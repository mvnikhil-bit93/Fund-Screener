"""Trusted server-side tenant context for pooled PostgreSQL transactions."""

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

import psycopg
from psycopg import Connection
from psycopg.pq import TransactionStatus
from psycopg.rows import TupleRow
from psycopg_pool import ConnectionPool

TenantPool = ConnectionPool[Connection[TupleRow]]
_CLEAR = "SELECT set_config('app.tenant_id', '', false)"


class UnsafeDatabaseRoleError(PermissionError):
    """The selected connection can bypass the application's tenant boundary."""


def _check_runtime_role(connection: Connection[TupleRow]) -> None:
    """Require a dedicated runtime login, including on reused connections."""
    result = connection.execute(
        """
        SELECT current_user = session_user
          AND COALESCE(pg_has_role(current_user, to_regrole('fi_runtime'), 'USAGE'), false)
          AND NOT EXISTS (
            SELECT 1 FROM pg_roles
            WHERE pg_has_role(current_user, oid, 'MEMBER')
              AND (rolsuper OR rolbypassrls OR rolcreatedb OR rolcreaterole OR rolreplication
                   OR rolname NOT IN (current_user, 'fi_runtime'))
          )
          AND NOT EXISTS (
            SELECT 1 FROM pg_database
            WHERE datname = current_database()
              AND pg_has_role(current_user, datdba, 'MEMBER')
          )
          AND NOT EXISTS (
            SELECT 1 FROM pg_namespace
            WHERE nspname IN ('app', 'catalog', 'ledger_migrations')
              AND (pg_has_role(current_user, nspowner, 'MEMBER')
                   OR has_schema_privilege(current_user, oid, 'CREATE'))
          )
          AND NOT EXISTS (
            SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname IN ('app', 'catalog', 'ledger_migrations')
              AND pg_has_role(current_user, c.relowner, 'MEMBER')
          )
        """
    ).fetchone()
    if result is None or result[0] is not True:
        raise UnsafeDatabaseRoleError(
            "Tenant connections require a dedicated, unprivileged fi_runtime login"
        )


def create_pool(dsn: str, *, min_size: int = 1, max_size: int = 4) -> TenantPool:
    """Open a bounded pool of restricted application connections."""
    # Fail immediately with a useful error instead of retrying an unsafe role
    # until the pool's startup timeout. New connections are checked again below.
    with psycopg.connect(dsn, autocommit=True, connect_timeout=5) as connection:
        _check_runtime_role(connection)
    pool: TenantPool = ConnectionPool(
        dsn,
        min_size=min_size,
        max_size=max_size,
        kwargs={"autocommit": True, "connect_timeout": 5},
        configure=_check_runtime_role,
        open=False,
    )
    try:
        pool.open(wait=True, timeout=5)
    except Exception:
        pool.close()
        raise
    return pool


@contextmanager
def tenant_connection(pool: TenantPool, tenant_id: UUID) -> Iterator[Connection[TupleRow]]:
    """Scope a request to an already-authorized tenant; authenticate before calling.

    The trusted backend supplies tenant_id. This is not a sandbox for arbitrary
    customer SQL: authentication and membership checks are introduced in M12.
    """
    if not isinstance(tenant_id, UUID):
        raise ValueError("tenant context requires a UUID")
    with pool.connection() as connection:
        if (
            not connection.autocommit
            or connection.info.transaction_status != TransactionStatus.IDLE
        ):
            raise ValueError("tenant context requires an idle autocommit connection")
        _check_runtime_role(connection)
        # A pool checkout must not inherit a previous session-level tenant.
        connection.execute(_CLEAR)
        try:
            with connection.transaction():
                connection.execute(
                    "SELECT set_config('app.tenant_id', %s, true)", (str(tenant_id),)
                )
                yield connection
        finally:
            if (
                not connection.closed
                and connection.info.transaction_status == TransactionStatus.IDLE
            ):
                connection.execute(_CLEAR)
