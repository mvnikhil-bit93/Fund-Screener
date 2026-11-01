# Fund-Screener

An auditable ETF competitor-intelligence platform, starting with a small universe
of active US equity ETFs. The active build contract is [MVP specification
v1.1](docs/spec.md); the [original specification](docs/reference/spec-v1.0.md)
retains the source golden numbers.

## Current stage

M01 establishes four Python package boundaries, pinned development tooling, the
original six-security fixture, and offline verification. M02 adds immutable ledger
records, explicit quality states, lossless Arrow schemas, and deterministic
record hashes. See [the data-contract reference](docs/data-contracts.md). M03 adds
a local PostgreSQL service, transactional migrations, catalog metadata, and
tenant tables with restricted roles and row-level security. See the
[database guide](docs/database.md) for setup and integration checks.

Financial engines, source adapters, snapshot publication, authentication, and the
UI are later tickets. The current golden tests validate the fixture's integrity
against the original specification; they do not validate implemented financial engines.
Source feasibility and access status are recorded in [docs/sources.md](docs/sources.md).
Local verification and remaining review gates are recorded in
[docs/decisions.md](docs/decisions.md).

## Local setup

Prerequisites: Python 3.12, uv, Git, and GNU Make. The cloud environment already
provides these. Database commands additionally require the local Docker daemon
at /var/run/docker.sock. Use the existing checkout; no worktree is necessary.

```sh
cd /workspace/Fund-Screener
make setup
make check
make golden
```

For another machine, run the same commands from its checkout directory.
Setup installs every workspace member and development dependency into .venv
using uv.lock. The initial installation needs approved package-registry access.
Make defaults UV_CACHE_DIR to .cache/uv inside the checkout so it works in the
cloud's writable workspace; an existing UV_CACHE_DIR setting takes precedence.
For a deliberate dependency change, update its allowlist reason, run uv lock,
then rerun setup/checks and review the lockfile changes together.

All check commands use uv in frozen, offline, no-sync mode after setup. A missing
environment fails rather than downloading dependencies during a check.

## Available commands

| Command | Purpose |
| --- | --- |
| make setup | Frozen installation of workspace and development dependencies |
| make check | All applicable offline checks |
| make lockcheck | Verify the lockfile matches current manifests, without network access |
| make lint | Ruff lint and formatting checks |
| make format | Apply Ruff formatting |
| make typecheck | Strict mypy over packages and tooling scripts |
| make boundaries | Import contracts and pure-engine import policy |
| make allowlist | Validate declared dependencies against documented policy |
| make test | Run offline tests |
| make golden | Validate the preserved golden fixture |
| make db-start | Start disposable PostgreSQL on 127.0.0.1:55432 |
| make db-status | Check the local database with a SQL query |
| make db-migrate | Bootstrap roles and migrate the local fund_dev database |
| make integration | Run real PostgreSQL migration, permission, and tenant-isolation tests |
| make db-stop | Remove the managed local database container and its temporary data |

Run make db-start before make integration. The integration suite creates and
removes isolated test databases; it is separate from make check and fails if its
configured database is unavailable. See [database.md](docs/database.md) for the
local trust-authentication boundary and restricted runtime login instructions.

There are intentionally no serve, ingest, rebuild, or deployment commands yet.
They will be introduced and verified with their tickets.

## Packages

| Distribution | Import namespace | Responsibility |
| --- | --- | --- |
| fund-ledger | ledger | Contracts, immutable storage, snapshot readers |
| fund-ingest | ingest | Fetch, parse, reconcile, and rebuild orchestration |
| fund-engines | engines | Pure deterministic analytics |
| fund-access | access | Authenticated query API and fixed web UI |

The allowlist covers direct runtime, development, optional, and build requirements;
the lockfile pins their resolved dependency graph. Import contracts enforce
package direction. The supplementary engine import check restricts engines to
the approved pure boundary; code review still checks behavioral purity.

## CI and review

GitHub Actions defines separate check, golden, PostgreSQL integration, and
secret-scanning jobs. CI can only be verified on GitHub after a commit is pushed.
Dependency installation is networked; tests use synthetic/recorded inputs, and
integration tests connect to an isolated PostgreSQL service. No deployment is
triggered by these workflows.

Before using main for reviewed development, configure branch protection in
GitHub: require passing CI, a human review, and CODEOWNERS review. CODEOWNERS
alone does not enforce a merge gate. CI does not provision infrastructure or
publish the cloud environment.

Follow [AGENTS.md](AGENTS.md) for implementation rules and the ticket dependencies
in the specification. External pilot readiness remains a separate milestone.
