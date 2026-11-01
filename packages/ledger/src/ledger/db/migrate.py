"""Transactional Alembic entry points with separate administrative role bootstrap."""

from pathlib import Path

import psycopg
from alembic import command
from alembic.config import Config
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict
from sqlalchemy import create_engine

ROLES = ("fi_owner", "fi_runtime", "fi_publisher")
_LOCK_KEY = 19037103


def _require_database(dsn: str) -> None:
    database = conninfo_to_dict(dsn).get("dbname")
    if not isinstance(database, str) or not database.strip():
        raise ValueError("migration operations require an explicit database name")


def bootstrap_roles(dsn: str) -> None:
    """Create NOLOGIN group roles, rejecting unsafe existing cluster identities.

    Requires an explicitly selected database and an administrative connection.
    No application login or password is provisioned here.
    """
    _require_database(dsn)
    with psycopg.connect(dsn) as connection:
        connection.execute("SELECT pg_advisory_xact_lock(%s)", (_LOCK_KEY,))
        for role in ROLES:
            row = connection.execute(
                "SELECT rolsuper, rolcreatedb, rolcreaterole, rolcanlogin, "
                "rolreplication, rolbypassrls FROM pg_roles WHERE rolname = %s",
                (role,),
            ).fetchone()
            if row is None:
                connection.execute(
                    sql.SQL(
                        "CREATE ROLE {} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE "
                        "NOREPLICATION NOBYPASSRLS"
                    ).format(sql.Identifier(role))
                )
            elif any(row):
                raise ValueError(f"existing role {role} has unsafe attributes")
        inherited = connection.execute(
            "SELECT member_role.rolname FROM pg_auth_members AS membership "
            "JOIN pg_roles AS member_role ON member_role.oid = membership.member "
            "WHERE member_role.rolname = ANY(%s)",
            (list(ROLES),),
        ).fetchall()
        if inherited:
            raise ValueError("foundation group roles must not inherit other roles")
        namespace = connection.execute(
            "SELECT pg_get_userbyid(nspowner) FROM pg_namespace WHERE nspname = 'ledger_migrations'"
        ).fetchone()
        if namespace is not None and namespace[0] != "fi_owner":
            raise ValueError("existing ledger_migrations schema has a different owner")
        database = connection.execute("SELECT current_database()").fetchone()
        assert database is not None
        connection.execute(
            sql.SQL("GRANT CREATE ON DATABASE {} TO fi_owner").format(sql.Identifier(database[0]))
        )
        connection.execute("CREATE SCHEMA IF NOT EXISTS ledger_migrations AUTHORIZATION fi_owner")
        connection.execute("REVOKE ALL ON SCHEMA ledger_migrations FROM PUBLIC")


def _migrate(dsn: str, target: str) -> None:
    # The URL has no credentials. The actual connection uses psycopg's native
    # DSN handling; neither credentials nor bound parameters are logged.
    _require_database(dsn)
    engine = create_engine(
        "postgresql+psycopg://",
        creator=lambda: psycopg.connect(dsn),
        hide_parameters=True,
    )
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql(f"SELECT pg_advisory_xact_lock({_LOCK_KEY})")
            connection.exec_driver_sql("SET LOCAL ROLE fi_owner")
            config = Config()
            config.set_main_option("script_location", str(Path(__file__).parent / "migrations"))
            config.attributes["connection"] = connection
            if target == "head":
                command.upgrade(config, target)
            else:
                command.downgrade(config, target)
    finally:
        engine.dispose()


def upgrade(dsn: str) -> None:
    """Upgrade to head atomically; callers bootstrap roles separately."""
    _migrate(dsn, "head")


def downgrade(dsn: str) -> None:
    """Explicitly remove the application/catalog schema to base for local tests."""
    _migrate(dsn, "base")


def revision(dsn: str) -> str | None:
    """Read the installed revision without creating any schema or table."""
    _require_database(dsn)
    with psycopg.connect(dsn) as connection:
        exists = connection.execute(
            "SELECT to_regclass('ledger_migrations.alembic_version')"
        ).fetchone()
        if exists is None or exists[0] is None:
            return None
        row = connection.execute(
            "SELECT version_num FROM ledger_migrations.alembic_version"
        ).fetchone()
        return str(row[0]) if row is not None else None
