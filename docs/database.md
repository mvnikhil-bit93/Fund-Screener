# PostgreSQL foundation

M03 provides catalog metadata, tenant tables, migrations, restricted database
roles, and a trusted-backend tenant transaction helper. It does not yet publish
holdings or authenticate users. The active contract is [M03 in the
specification](spec.md); implementation decisions are in [decisions.md](decisions.md).

## Local service and checks

Run from the repository root after installing Python 3.12, uv, GNU Make, and
Docker. The helper requires Docker's local socket at /var/run/docker.sock and
selects it explicitly, ignoring ambient Docker host/context/TLS selectors.

```sh
make setup
make db-start
make db-status
make db-migrate
make integration
make check
make golden
```

make db-start creates or reuses the recognized fund-screener-postgres container
and waits for a successful SQL query. make db-status repeats that readiness
check. make db-migrate bootstraps roles and upgrades only its fixed local
fund_dev database; it clears ambient libpq routing/service options first. A
successful migration reports revision 0001_foundation. Repeating these commands
does not create a second container or reapply an installed revision.

The service binds only 127.0.0.1:55432 and uses trust authentication. Its data
directory is tmpfs, with no persistent host volume. This is an isolated,
disposable development/test service: processes that can reach its local port
can connect as the PostgreSQL administrator. Do not use it for sensitive data,
shared services, or a deployed database. No application login is created by
startup or migration.

Stop and remove the container when finished:

```sh
make db-stop
```

Stopping discards all local data, roles, and migration state. A later start
creates an empty cluster, so run make db-migrate again. The helper verifies the
container label, image, and port mapping before changing it, and refuses a
conflicting container with the same name. Other containers are unaffected.

The local helper and CI pin the same official image:

```text
postgres:17-bookworm@sha256:839fbb5a4942a7758dd93e18b42ea5649807491a0545b5eeeb8f0b8bb11857a5
```

An initial image pull needs registry access. Review updates to the digest in
scripts/local_postgres.py and .github/workflows/ci.yml together and rerun the
database checks. A PostgreSQL major-version upgrade needs its own migration and
compatibility review.

make check and make golden use offline fixtures and need no running database.
make integration uses real PostgreSQL connections and fails when its configured
server is missing; it does not silently skip database coverage. The default is:

```text
FI_TEST_ADMIN_DSN=postgresql://postgres@127.0.0.1:55432/postgres
```

Each integration test allocates a unique fi_test_* database and restricted login
roles, then removes those resources on completion. Tests do not migrate or seed
fund_dev. Bootstrap group roles are cluster-wide and remain until the disposable
cluster is removed. Use only a disposable local trust-authenticated PostgreSQL
server with this fixture. An explicit loopback host or Unix socket is required;
remote host addresses and service-based routing are rejected. CI starts a
separate service with the same image and runs make integration independently of
the offline checks.

## Migration API

ledger.db.migrate exposes four functions, each taking a PostgreSQL DSN with an
explicit, nonblank database name:

| Function | Behavior |
| --- | --- |
| bootstrap_roles(dsn) | Administrative role validation/creation and migration-schema bootstrap |
| upgrade(dsn) | Transactional Alembic upgrade to head; repeat calls at head are harmless |
| downgrade(dsn) | Transactional downgrade to base, deleting the app and catalog tables and their data |
| revision(dsn) | Read the installed revision, or None before upgrade/after downgrade |

The functions do not create the target database or fall back to a username-named
database. Bootstrap requires an administrative connection and creates three
NOLOGIN groups plus the ledger_migrations schema. Existing groups with elevated
attributes or inherited memberships are rejected. A migration connection must
be able to SET ROLE fi_owner; application runtime credentials cannot do this.

Role bootstrap is a separate committed operation. Each upgrade/downgrade runs
inside one transaction under fi_owner and takes an advisory transaction lock.
A failed revision rolls back that revision's schema changes and version update;
the earlier bootstrap is retained. Downgrade preserves the group roles and
ledger_migrations schema. It is a destructive test/reset operation, not a
backup or data-recovery mechanism. revision is read-only and creates nothing.

## Schema and role boundaries

| Object | Foundation contract |
| --- | --- |
| catalog.dataset_versions | Lowercase 64-character hex data_version primary key, JSON object manifest, schema and code versions |
| catalog.catalog_commits | One commit per data_version, unique UUID run_id, optional parent pointing to a catalog commit, timestamp metadata |
| catalog.current_dataset | At most one row; its pointer must reference a catalog commit |
| app.tenants | UUID tenant_id primary key and name |
| app.memberships | Tenant and subject composite key; owner or analyst role |
| app.baskets | Tenant and UUID basket_id composite key, name, text-array fund IDs |
| app.audit_log | Tenant and UUID event_id composite key, actor/action, JSON object payload, timestamp |

| Group | Allowed operations |
| --- | --- |
| fi_owner | Own the schemas/tables and run migrations; never grant to runtime or publisher logins |
| fi_runtime | SELECT catalog and tenant tables; INSERT/UPDATE/DELETE tenant baskets; INSERT tenant audit rows |
| fi_publisher | SELECT/INSERT catalog data and commits; INSERT/UPDATE current pointer; required commit-sequence access |

The runtime cannot change tenants or memberships, mutate existing audit rows,
truncate tenant tables, write the catalog, or assume the owner/publisher role.
The publisher has no app privileges and cannot update/delete historical dataset
or commit rows. Explicit grants/revokes prevent permissive owner default table
or sequence ACLs from exposing these objects through PUBLIC.

All four app tables enable and force row-level security. Policies check
app.tenant_id for both reads and writes; missing or empty context exposes no
tenant rows. Composite keys allow the same basket/event identifier in different
tenants without changing the tenant boundary. The catalog is global and has no
tenant RLS policy.

## Restricted local runtime login

After make db-migrate, provision a dedicated login once per fresh local cluster:

```sh
uv run --frozen --offline --no-sync python - <<'PY'
import psycopg

dsn = "postgresql://postgres@127.0.0.1:55432/fund_dev?hostaddr=127.0.0.1"
with psycopg.connect(dsn) as connection:
    connection.execute(
        "CREATE ROLE fund_runtime LOGIN INHERIT NOSUPERUSER NOCREATEDB "
        "NOCREATEROLE NOREPLICATION NOBYPASSRLS"
    )
    connection.execute("GRANT fi_runtime TO fund_runtime")
    connection.execute("GRANT CONNECT ON DATABASE fund_dev TO fund_runtime")
PY
```

This intentionally fails if that login already exists, allowing its privileges
to be reviewed instead of silently accepting an existing identity. Local trust
authentication needs no password. Deployment credentials and authentication
configuration are separate future work; never reuse trust authentication there.

Use postgresql://fund_runtime@127.0.0.1:55432/fund_dev for application connections.
Keep administrator and publisher DSNs separate. If a publisher login is needed
for local work, create another equally restricted login and grant only
fi_publisher; never combine runtime, publisher, and owner membership.

access.db.create_pool opens a pool of dedicated fi_runtime connections. It
rejects elevated roles, database ownership, ownership/creation privileges in
the foundation schemas, extra role memberships, and sessions using SET ROLE.
The check also runs when tenant_connection checks out a connection.
access.db.tenant_connection(pool, tenant_id) requires a UUID, clears stale
session context, starts a transaction, sets the tenant locally, and clears
context again after commit or rollback.

The trusted backend must authenticate the caller and authorize tenant membership
before supplying this UUID. Do not select it directly from an unverified request
field or expose arbitrary customer SQL through these connections. A UUID type
check and RLS policy do not prove membership. M12 adds the authentication and
membership enforcement; there is no authenticated application endpoint yet.

## Deferred publication behavior

M03 establishes catalog relationships and grants. It does not calculate a
physical manifest hash, validate manifest contents beyond a JSON object, store
holdings objects, publish a dataset atomically, or resolve a point-in-time read.
The hash-shaped data_version column does not prove that an object matches its
content hash. Parent and current-pointer foreign keys require a corresponding
catalog commit row, including rows created earlier in the same transaction.

committed_at and occurred_at currently default to statement_timestamp(). A
catalog row timestamp is statement-time metadata, not proof of transaction
commit order or knowledge availability. M07 must establish publication locking,
crash safety, idempotent retries, manifest/hash verification, and the exact
knowledge-cutoff/timestamp rules before readers rely on this catalog.

These local commands and CI checks do not deploy infrastructure or publish the
cloud environment. Production access, durability, recovery, and deployment
remain later reviewed milestones in the specification.
