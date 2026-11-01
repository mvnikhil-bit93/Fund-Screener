# Implementation decisions and evidence

## 1 November 2026 — M01 scaffold

M01 is implemented and verified locally. Nikhil explicitly requested publishing
this initial scaffold to GitHub. M00 remains blocked by source network access;
see [sources.md](sources.md).

The remote had no branches at the publication preflight, so this is the initial
main bootstrap rather than a pull request against an existing base. Subsequent
implementation tickets should use feature branches and pull requests. GitHub CI
and secret scanning are configured; the local evidence below does not establish
their hosted results. Publication to GitHub does not deploy the application or
publish the cloud environment.

### Implemented

- Python 3.12 uv workspace with ledger, ingest, engines, and access namespaces.
- Locked development/build dependencies and checks covering direct runtime,
  optional, development-group, and build requirements.
- Package-direction contracts and a conservative static import check for pure
  engines and ledger type modules. Static checks supplement behavioral review;
  they do not certify arbitrary Python as pure.
- Original six-security fixture, including all deferred attribution expectations.
- CI definitions, ownership/review guidance, and the local setup/check commands.

No financial engine, source adapter, database service, authentication service, or
web application is implemented in this ticket.

### Verification

Executed with Python 3.12.14 and uv 0.12.23:

| Check | Result |
| --- | --- |
| Frozen make setup | Passed; repeated setup found the environment current |
| make check | Passed: lock consistency, Ruff lint/format, strict mypy, four import contracts, import policy, dependency allowlist, and 30 tests |
| make golden | Passed: 9 fixture-integrity tests, also included in the 30 above |
| Deliberate forbidden import | Actual import-linter CLI rejected an engine importing access in an isolated temporary copy |
| Dependency and pure-import rejection cases | Passed for unapproved direct/extra/group/build dependencies and disallowed engine imports/calls |
| Original archived spec | Byte-identical to the uploaded v1.0 after final verification |

These fixture tests verify transcription from the original document. They do not
claim to validate unimplemented financial engines.

The original archive SHA-256 is
6d66f67acba2a27d269a546c527739763c20bee9d3abb730dd5ac3fddca51bc3.

### Setup decisions

Make uses a workspace-local uv cache by default because the cloud home directory
is read-only. An explicitly supplied UV_CACHE_DIR remains respected.

Ruff excludes docs/reference: the archive is source evidence and must not be
rewritten by formatting, including formatting of embedded Python examples.

The environment configuration draft now contains the tested installation steps:
change to /workspace/Fund-Screener, run make setup, then make check. No service
startup instruction is required yet. The draft also contains the two source
hostname additions recorded in sources.md. Saving the draft does not apply it or
publish the prepared environment.

### Next dependency-ready work

M02 can add typed snapshot/instrument contracts, canonical hashes, and explicit
quality states using synthetic inputs. M00 can resume after the issuer domains
are enabled through environment settings. Source coverage, permissions, and
production readiness remain unverified.
