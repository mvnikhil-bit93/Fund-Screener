"""Alembic environment driven exclusively by an explicitly supplied connection."""

from alembic import context
from sqlalchemy.engine import Connection

connection = context.config.attributes.get("connection")
if not isinstance(connection, Connection):
    raise RuntimeError("use ledger.db.migrate with an explicit database connection")

context.configure(
    connection=connection,
    version_table_schema="ledger_migrations",
    transactional_ddl=True,
)
with context.begin_transaction():
    context.run_migrations()
