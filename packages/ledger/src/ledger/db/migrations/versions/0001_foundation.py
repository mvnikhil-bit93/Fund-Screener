"""Catalog metadata and tenant application foundation with forced RLS."""

from alembic import op

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA catalog AUTHORIZATION fi_owner")
    op.execute("CREATE SCHEMA app AUTHORIZATION fi_owner")
    op.execute("REVOKE ALL ON SCHEMA catalog, app FROM PUBLIC")
    op.execute(
        """
        CREATE TABLE catalog.dataset_versions (
            data_version text PRIMARY KEY CHECK (data_version ~ '^[0-9a-f]{64}$'),
            manifest jsonb NOT NULL CHECK (jsonb_typeof(manifest) = 'object'),
            schema_version text NOT NULL CHECK (btrim(schema_version) <> ''),
            code_version text NOT NULL CHECK (btrim(code_version) <> '')
        )
        """
    )
    op.execute(
        """
        CREATE TABLE catalog.catalog_commits (
            commit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            data_version text NOT NULL UNIQUE REFERENCES catalog.dataset_versions(data_version),
            parent_version text REFERENCES catalog.catalog_commits(data_version),
            run_id uuid NOT NULL UNIQUE,
            committed_at timestamptz NOT NULL DEFAULT statement_timestamp(),
            CHECK (parent_version IS NULL OR parent_version <> data_version)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE catalog.current_dataset (
            singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
            data_version text NOT NULL REFERENCES catalog.catalog_commits(data_version)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE app.tenants (
            tenant_id uuid PRIMARY KEY,
            name text NOT NULL CHECK (btrim(name) <> '')
        )
        """
    )
    op.execute(
        """
        CREATE TABLE app.memberships (
            tenant_id uuid NOT NULL REFERENCES app.tenants(tenant_id),
            subject text NOT NULL CHECK (btrim(subject) <> ''),
            role text NOT NULL CHECK (role IN ('owner', 'analyst')),
            PRIMARY KEY (tenant_id, subject)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE app.baskets (
            tenant_id uuid NOT NULL REFERENCES app.tenants(tenant_id),
            basket_id uuid NOT NULL,
            name text NOT NULL CHECK (btrim(name) <> ''),
            fund_ids text[] NOT NULL DEFAULT '{}',
            PRIMARY KEY (tenant_id, basket_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE app.audit_log (
            tenant_id uuid NOT NULL REFERENCES app.tenants(tenant_id),
            event_id uuid NOT NULL,
            actor text NOT NULL CHECK (btrim(actor) <> ''),
            action text NOT NULL CHECK (btrim(action) <> ''),
            payload jsonb NOT NULL DEFAULT '{}' CHECK (jsonb_typeof(payload) = 'object'),
            occurred_at timestamptz NOT NULL DEFAULT statement_timestamp(),
            PRIMARY KEY (tenant_id, event_id)
        )
        """
    )
    for table in ("tenants", "memberships", "baskets", "audit_log"):
        op.execute(f"ALTER TABLE app.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE app.{table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation ON app.{table} TO fi_runtime "
            "USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) "
            "WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)"
        )
    # Owner-level default ACLs must not silently widen this revision's grants.
    op.execute(
        "REVOKE ALL ON ALL TABLES IN SCHEMA app, catalog FROM PUBLIC, fi_runtime, fi_publisher"
    )
    op.execute(
        "REVOKE ALL ON ALL SEQUENCES IN SCHEMA catalog FROM PUBLIC, fi_runtime, fi_publisher"
    )
    op.execute("GRANT USAGE ON SCHEMA catalog TO fi_runtime, fi_publisher")
    op.execute(
        "GRANT SELECT ON catalog.dataset_versions, catalog.catalog_commits, "
        "catalog.current_dataset TO fi_runtime, fi_publisher"
    )
    op.execute(
        "GRANT INSERT ON catalog.dataset_versions, catalog.catalog_commits, "
        "catalog.current_dataset TO fi_publisher"
    )
    op.execute("GRANT UPDATE ON catalog.current_dataset TO fi_publisher")
    op.execute(
        "GRANT USAGE, SELECT ON SEQUENCE catalog.catalog_commits_commit_id_seq TO fi_publisher"
    )
    op.execute("GRANT USAGE ON SCHEMA app TO fi_runtime")
    op.execute(
        "GRANT SELECT ON app.tenants, app.memberships, app.baskets, app.audit_log TO fi_runtime"
    )
    op.execute("GRANT INSERT, UPDATE, DELETE ON app.baskets TO fi_runtime")
    op.execute("GRANT INSERT ON app.audit_log TO fi_runtime")


def downgrade() -> None:
    op.execute("DROP TABLE app.audit_log, app.baskets, app.memberships, app.tenants")
    op.execute("DROP SCHEMA app")
    op.execute(
        "DROP TABLE catalog.current_dataset, catalog.catalog_commits, catalog.dataset_versions"
    )
    op.execute("DROP SCHEMA catalog")
