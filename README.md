# Fund-Screener

An auditable ETF competitor-intelligence platform, starting with a small universe
of active US equity ETFs. The active build contract is [MVP specification
v1.1](docs/spec.md); the [original specification](docs/reference/spec-v1.0.md)
retains the source golden numbers.

## Current stage

M01 establishes four Python package boundaries, pinned development tooling, the
original six-security fixture, and offline verification. The packages are
namespaces for future implementation, not running services.

Financial engines, source adapters, databases, authentication, and the UI are
later tickets. The current golden tests validate the fixture's integrity against
the original specification; they do not validate implemented financial engines.
Source feasibility and access status are recorded in [docs/sources.md](docs/sources.md).
Local verification and remaining review gates are recorded in
[docs/decisions.md](docs/decisions.md).

## Local setup

Prerequisites: Python 3.12, uv, Git, and GNU Make. The cloud environment already
provides these. Use the existing checkout; no worktree is necessary.

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

There are intentionally no serve, ingest, rebuild, database integration, or
deployment commands yet. They will be introduced and verified with their tickets.

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

GitHub Actions defines separate check, golden, and secret-scanning jobs. CI can
only be verified on GitHub after a commit is pushed. Dependency installation is
networked; test execution uses offline fixtures. No deployment is triggered by
these workflows.

Before using main for reviewed development, configure branch protection in
GitHub: require passing CI, a human review, and CODEOWNERS review. CODEOWNERS
alone does not enforce a merge gate. CI does not provision infrastructure or
publish the cloud environment.

Follow [AGENTS.md](AGENTS.md) for implementation rules and the ticket dependencies
in the specification. External pilot readiness remains a separate milestone.
