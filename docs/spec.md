# Fund intelligence platform — MVP build specification v1.1

Date: 1 November 2026  
Owner: Nikhil  
Status: active MVP build contract; progress and verification are in docs/decisions.md  
Repository: Fund-Screener; use the existing checkout

Scope amendments: 7 November 2026 — approved identified money-market fund units and daily historical holdings for at least three years, or since inception for newer funds.

## 1. Purpose and relationship to v1.0

Build a trustworthy daily competitor-intelligence product for a small universe of active US equity ETFs. The first release helps a product or distribution analyst compare reported portfolios, understand concentration and overlap, and see what changed between disclosures.

This specification replaces v1.0 as the proposed MVP build contract. The original is preserved unchanged at [reference/spec-v1.0.md](reference/spec-v1.0.md). Original golden inputs and expected numbers remain authoritative for the matching financial cases; the attribution fixture is retained for a later release.

Version 1.0 remains a vision document. Its deployment instructions, package list, approval loops, and ticket sequence are not active instructions for this revision. This document establishes implementation defaults, not claims that sources, licensing, infrastructure, or production behavior have been validated.

Implementation began after Nikhil's instruction to proceed to the next step. Follow the ticket dependencies below; that instruction does not authorize deployment or publication.

## 2. Product boundary

### Primary user and workflow

A product or distribution analyst maintains a basket of competing active equity ETFs. Each morning they can:

1. See which funds have a new complete disclosure and which are delayed.
2. Inspect reported sector and issuer-domicile exposures, concentration, and pairwise overlap.
3. Compare two portfolio dates and inspect new, absent, and materially changed reported positions.
4. Open the source and calculation provenance for each result.
5. Read a deterministic daily brief linking to the relevant views.

The product says “reported holdings changes.” A weight change alone does not establish a purchase, sale, trade date, or manager intention.

### Launch universe

- Target 10–25 explicitly named, US-listed, USD-reporting, active, long-only equity ETFs from one or two issuers.
- Support ordinary equity, documented ADR mappings, explicitly reported USD cash, and identified money-market fund share classes held as direct securities.
- Money-market fund units retain their own instrument identity and reported weight. They are not Cash, are not looked through, and are not assumed interchangeable or valued at par. A source label alone does not establish a verified fund/share-class identity.
- Exclude short, leveraged, inverse, option-overlay, futures, swap, and other derivative strategies from the initial roster.
- A fund advertised as an equity fund is not automatically supported. Its actual positions and disclosure format must satisfy the adapter contract.
- Initial issuer discovery started with Capital Group and Avantis Investors. The current historical-source investigation order is in [historical-sources.md](historical-sources.md); research priority does not establish access, daily completeness, or permitted commercial use.
- M00 produces the exact fund identifiers, source URLs, selected issuers, and coverage decisions. Do not invent a production roster or substitute another universe silently.
- Every launch fund requires complete daily historical holdings for at least the three calendar years ending on its latest expected portfolio date, or since documented inception if newer. Use the fund's publication calendar; stale availability cannot move the required window backward. Establish credible historical sourcing before choosing the first adapter.
- A first issuer is sufficient for the pilot if it supports at least ten eligible funds. Add a second only after the first adapter works end to end.

### Included in the pilot

- Immutable raw documents and complete, revisioned holdings snapshots.
- Stable instrument identities; evidence-backed identifier mappings.
- One reviewed, versioned sector taxonomy and one issuer-domicile taxonomy.
- Exposure, overlap, concentration, and disclosure-change calculations.
- Saved baskets; a small authenticated web UI and read-only query API.
- A daily brief rendered from computed tables; optional email delivery once configured.
- Per-fund freshness, source completeness, mapping coverage, provenance, and operational health.
- Tenant-scoped baskets, users, credentials, and query/audit records.

### Deferred

N-PORT ingestion; UCITS coverage; fixed-income and derivative analytics; holdings attribution; factor regression; manager feeds; Names Rule compliance; arbitrary user taxonomies; AI classification; natural-language queries; MCP; a licensed bulk data feed; strategy/share-class inference; enterprise SSO features beyond ordinary managed OIDC login; Temporal; Redis; gold pre-aggregations; and a general dashboard builder.

These are separate product expansions, not hidden MVP acceptance criteria.

The deferral of a licensed bulk data feed does not preclude M00 research into commercial historical holdings sources. Source evaluation does not authorize purchasing, implementing or enabling a feed, contacting providers, or redistributing bulk data. Record any selected commercial delivery proposal and its implementation implications before proceeding.

## 3. Success criteria and budget

Technical correctness is necessary, but the pilot must also answer a recurring customer question.

- One prospective user can create a competitor basket, explain a reported change from its source, and use the brief on at least five market days. Nikhil records feedback and decides whether the workflow is useful enough to expand.
- At least ten eligible funds have valid coverage for five consecutive expected publication days before pilot sign-off.
- Before pilot sign-off, reconcile the full acquired historical backfill for every launch fund to its approved coverage inventory and publication calendar. Unresolved missing expected dates block a claim that the historical minimum is met. Report source availability and analytical eligibility separately; historical unsupported positions or incomplete weights cannot be hidden to manufacture coverage.
- Every scheduled run reports coverage gaps; missing data never appears as zero exposure or “no changes.”
- Supported, executed calculations match deterministic expected results within their declared tolerances. There is no allowance for a percentage of incorrect financial answers.
- p95 response time for a 25-fund, two-date query is below two seconds on a documented 2-vCPU, 4-GiB benchmark machine with local snapshot files, excluding login and source retrieval.
- Measure cold object-storage reads separately. Report both cold and warm timings; do not relabel warm-cache results as universal latency.
- Target recurring operating costs below US$1,500/month. Before external pilot access, produce a priced estimate covering hosting, storage, database, identity, email, source/reference-data rights, and support services.
- Use budget alerts at US$500 and US$1,000. An alert is not a spending cap; scheduled ingestion must also have request, file-size, retry, and runtime limits.

No current vendor price, regulatory deadline, or source right is assumed verified by this document.

## 4. Minimal architecture

### Chosen stack

| Concern | MVP choice |
| --- | --- |
| Language and tooling | Python 3.12, uv with a committed lockfile |
| Data contracts | Pydantic v2 and explicit Arrow schemas |
| Deterministic analytics | Polars; NumPy only if a concrete calculation needs it |
| Raw and analytical objects | Immutable files locally; S3 objects for hosted environments |
| Catalog and application state | PostgreSQL with migrations, transactional publication metadata, and RLS for tenant records |
| API and web UI | FastAPI, Jinja2 templates with autoescape, small bundled JavaScript |
| Authentication | Managed OIDC using Cognito and Authlib; scoped API keys for programmatic access |
| Batch processing | A bounded Python CLI, one scheduled worker, a PostgreSQL-backed job/publication record |
| Initial scheduling | Explicit local command in development; EventBridge Scheduler invoking an ECS task when deployed |
| Hosted runtime | One API task and scheduled worker tasks on ECS Fargate, S3, and a small managed PostgreSQL instance |
| Observability | Structured logs, health endpoints, run records, and basic provider metrics |

No frontend build toolchain, dedicated cache service, workflow platform, or LLM is required to prove the pilot.

The hosting choice is a starting design subject to the cost gate. Include ingress, networking, backups, logs, and database costs in that decision.

### Repository structure after the scaffold ticket

~~~text
Fund-Screener/
  AGENTS.md
  README.md
  pyproject.toml
  uv.lock
  Makefile
  .python-version
  .importlinter
  .github/workflows/ci.yml
  .github/pull_request_template.md
  .github/CODEOWNERS
  docs/
    spec.md
    reference/spec-v1.0.md
    sources.md
    decisions.md
    methodology/
    operations.md
    costs.md
  packages/
    ledger/src/ledger/
    ingest/src/ingest/
    engines/src/engines/
    access/src/access/
    access/src/access/templates/
    access/src/access/static/
  tests/
    golden/
    recorded/
    integration/
    fixtures/
  scripts/
  infra/
~~~

Create files when their ticket gives them meaningful content. Do not add empty deployment modules or artificial passing tests to populate the tree.

### Package boundaries

- ledger owns types, canonicalization, immutable-object I/O, catalog operations, and point-in-time readers. It must not import ingest, engines, or access.
- ingest owns fetch, parse, source validation, identity preparation, and rebuild orchestration; it calls ledger. It must not import access or engines.
- engines may import ledger.types and pure calculation dependencies only. No filesystem, database, network, process environment, random state, or clock access.
- access owns authenticated HTTP/UI behavior and tenant application state. It reads through ledger readers and calls engines. It must not call ingest internals.
- The rebuild entry point is ingest.rebuild, not ledger.rebuild.
- No code outside ledger reads published holdings Parquet directly. No template computes financial values.

## 5. Source contracts, rights, and observations

M00 records each proposed source in docs/sources.md with:

- issuer and fund identifiers; authoritative document endpoint and approved redirect hosts;
- what the file represents: full portfolio, valuation date, weight units and denominator, supported instrument categories;
- expected market calendar, holiday exceptions, publication window, timezone, and fund-specific deadline;
- schema and parser version; expected source identifiers; decimal precision and documented rounding behavior;
- evidence for download, retention, display, and commercial-use permissions, with review date and owner;
- separate redistribution permission status; no bulk feed is enabled by this pilot;
- freshness semantics and completeness checks;
- a recent permitted fixture with URL, retrieval time, content hash, and source portfolio date.

Historical sourcing is an M00 prerequisite to adapter selection. The [historical-source assessment](historical-sources.md) records candidate evidence and remaining gaps. For each proposed launch fund, obtain a dated inventory of available portfolio dates across the required three-year/since-inception window, supported by source evidence and checked against the expected calendar. Inspect actual historical samples spanning the window and a consecutive-date interval, including at least two distinct permitted portfolio dates from the first source. Document original provenance, identifier continuity, corrections/restatements, delivery limits, retention/use conditions, and quoted or measured costs, including one-time backfill and recurring charges. Provider reputation or an advertised dataset start date is not fund-specific coverage evidence.

M00 establishes feasibility through the coverage inventory and representative samples; it does not require an unbuilt production importer to acquire the entire archive. Full acquisition and reconciliation follow implementation and remain a data-pilot gate. Daily price/NAV history, periodic filings, top holdings, creation baskets, proxy portfolios, or reconstructed estimates do not satisfy the daily full-portfolio requirement. Missing dates must remain explicit, without silent carry-forward or interpolation. Historical fund and instrument changes require evidence; do not splice separate funds across mergers or imply that a current-fund roster removes survivorship bias.

Backfill preserves the knowledge-time rules in section 6: first_observed_at is the actual acquisition time, and source_published_at requires separate evidence. Retrospective portfolio-date coverage does not establish what this system knew on those historical dates. Evaluate revision and publication metadata without silently introducing a historical source-publication-time research mode.

Measure total weights, reported precision, and full-overlap eligibility on the source samples. The pilot must demonstrate useful comparison output on actual files. If rounding means most files are ineligible for full overlap/active share under section 8, record that limitation before committing to the source: the pilot may use clearly labeled known matched weights, or adopt a separately reviewed methodology. Do not silently normalize source weights or relax a numerical gate.

Public access is not redistribution permission. A source whose rights remain unresolved may be investigated as permitted, but cannot silently become a customer-facing production dependency. The same review applies to identifiers and sector classifications. Do not assume rights to GICS or any other proprietary taxonomy.

Use a small internally defined sector vocabulary and manually reviewed mappings with documented source evidence. The launch taxonomy is single-label and has one sector level; issuer domicile means legal issuer domicile, not exchange location or economic revenue exposure.

Crawlers must honor applicable access terms and rate limits; use identifiable contact headers when required, bounded retries, timeouts, approved redirects, maximum response sizes, and decompression limits. Check freshness and schema per fund, not merely per issuer.

Tests use recorded or synthetic inputs. Capturing new permitted fixtures and running live source checks are explicit integration operations, not unit tests.

## 6. Canonical data and time

### Core records

| Record | Required content |
| --- | --- |
| source_document | document_id, source_id, fund_id, exact content hash, immutable object path, fetched_at UTC, optional evidenced source_published_at UTC, content type, adapter version |
| snapshot | snapshot_id, fund_id, asof_date, source_document_id, first_observed_at UTC, source_revision, portfolio-completeness status, weight basis, total weight, quality reasons, parser version |
| position | snapshot_id, position_id, instrument_id, source row reference, original identifiers/name, asset category, reported weight, optional quantity/market value/currency/NAV-derived weight |
| instrument | stable internal instrument_id, supported asset type, origin and evidence references |
| identity_mapping | mapping_version, available_at UTC, external identifier namespace/value, instrument_id or explicit equivalence, evidence, reviewer |
| taxonomy_mapping | taxonomy_id, version, available_at UTC, instrument_id, node_id, evidence, reviewer; immutable after publication |
| fund_source_schedule | fund_id, source_id, calendar version, source timezone, expected dates, publication deadline rule |
| quality_run | run_id, checked_at UTC, fund/date coverage, source/parser/mapping status, exception details |
| dataset_manifest | data_version, sorted object hashes, retained snapshot/revision membership, retained identity/taxonomy version references, schema and code versions |
| catalog_commit | data_version, parent version, committed_at UTC, publishing run and outcome; operational metadata outside the content hash |

Schema details may evolve through reviewed migrations, but the identity, snapshot, and temporal contracts below are mandatory.

### Complete snapshot semantics

A snapshot is the complete set of positions disclosed for one fund and one portfolio date. A revision replaces that whole disclosed set for that date.

Do not interpret an absent security as “carry its last row forward.” A security absent from the selected complete snapshot is absent from that portfolio. Multiple source rows for one instrument retain position-level provenance and aggregate only when calculations require it.

Malformed, incomplete, or quarantined candidates cannot supersede an accepted complete snapshot. They remain in bronze and quality records.

Source completeness and numerical completeness are separate facts. A complete published file may contain a visible unexplained weight residual.

### Knowledge time

- asof_date is the source's portfolio valuation date.
- first_observed_at is when this system first successfully obtained the exact source revision.
- source_published_at is optional and must have evidence; do not infer it from an as-of date or backdate an archive download.
- A committed version also records when parsed snapshots and reference mappings became available to queries.
- Historical-as-known queries require both first observation and catalog publication to be no later than the requested UTC knowledge cutoff. This conservatively models what this system could have answered.
- Backfilled documents enter knowledge history when acquired and published. A future source-publication-time research mode needs a separately specified evidence standard.

### Snapshot selection

Given fund_id, requested portfolio date D, knowledge cutoff K, and an immutable dataset manifest:

1. Consider only accepted complete snapshots present in that manifest, with asof_date <= D and knowledge availability <= K.
2. Select the greatest eligible asof_date.
3. Within that date select the greatest eligible accepted source revision.
4. Return every position from that snapshot and no position from another snapshot.
5. Return its actual date, revision, observation/publication times, and whether it satisfies the caller's freshness requirement.

No eligible snapshot is an explicit unavailable result. An exact-date request cannot be satisfied by an older portfolio. For a basket, the default comparison requires the requested date for every included fund; an explicit allow_latest mode reports per-fund dates and the unavailable funds.

Source amendments use an explicit supersedes relationship and deterministic revision order. Two observed revisions on the same day are distinguishable by UTC time and revision identity.

### Reference-data history

Historical-as-known results use identity and taxonomy mappings available by K. A user may explicitly request a restated analysis of an old portfolio with a newer mapping, but the result must be labeled restated and record that newer reference cutoff.

Restated mode requires an explicit reference_known_by UTC cutoff. Holdings still use the original known_by cutoff; only reference mappings use reference_known_by. As-known mode uses known_by for both and rejects an explicit taxonomy/reference version that was unavailable then.

Every result pins the dataset, selected snapshots, identity mapping, taxonomy mapping, methodology versions, and normalized query. An old result must never be re-rendered with a newer classification silently.

Each manifest retains references to the earlier snapshot revisions and reference-data versions within the agreed retention window. Selecting a newer manifest therefore does not remove the history required by an earlier knowledge cutoff. Requests for history outside retained coverage return an explicit unavailable reason.

## 7. Identity, cash, and classification

instrument_id is the internal join key. FIGI, ISIN, CUSIP, ticker, and issuer security IDs are external identifiers with namespace, evidence, and versioned mappings.

- Preserve listing/currency distinctions where they change instrument identity. Do not collapse exchange identifiers into one price-bearing instrument without an explicit rule.
- Prefer verified identifiers; ambiguous candidates enter a review queue.
- A provisional identity is source-scoped and based on stable source identifiers and discriminating fields. A normalized name alone is never sufficient.
- Do not assume provisional identities from different sources represent the same security.
- If continuity between dates cannot be established, mark the affected comparison unresolved and suppress activity assertions for those positions.
- Mapping corrections are separate events. Resolve both endpoints through the same pinned identity mapping so an identity change does not become a false new/exit event.
- Reported USD cash maps to an explicit Cash node and may overlap with reported USD cash. An unexplained residual is never Cash.
- Identified money-market fund share classes use the distinct money_market_fund asset category. Preserve each share class's identity, quantity, market value and reported weight. Match only the same confidently resolved instrument; do not merge different money-market funds or match them to Cash by asset category.
- Money-market units remain non-cash securities for concentration and classification coverage. Do not look through to underlying holdings or infer a sector/domicile from the sponsor. Unreviewed mappings remain Unclassified with their reported weight preserved.
- This extension does not support arbitrary pooled funds, signed-negative-cash analytics, foreign-currency cash or derivatives. Those rows remain candidate evidence with their existing eligibility restrictions.
- Sector and issuer-domicile taxonomies are independent. Missing classifications retain their full weight in Unclassified.
- Changes to mappings publish new versions; they do not mutate older results.

No LLM guesses identifiers or classifications in the MVP.

## 8. Weights, quality, and financial methods

### Weight basis and numerical rules

Weights are decimal fractions, never percentages. Parse reported decimals without losing their original precision. Missing weights are not zero.

Retain reported_weight and its declared denominator. When compatible market values and net assets exist, retain calculated_nav_weight and the reconciliation difference separately. Issuer-reported weights must not be described as independently reconciled.

The MVP's analytical weights are the source-reported weights. NAV-derived weights are diagnostic only. The adapter records the reported denominator; cross-fund comparisons require comparable denominators. Record the basis in requests/results; do not mix NAV weights with weights normalized over a subset of assets.

Use float64 for engine operations, deterministic ordering, and absolute comparison tolerance 1e-9 for the original golden cases. Preserve original decimal strings for threshold and source-rounding checks.

Let W be the sum of admitted reported analytical weights and residual = 1 - W.

- Never normalize W to one just to pass a check.
- Retain and display W and residual, including a negative residual when the file overstates total weight.
- Residual is a diagnostic, not a security, cash position, or invented balancing line.
- An unexplained absolute residual above 0.01 quarantines the candidate under the default launch contract. Source-specific stricter limits are allowed; any relaxation needs a documented methodological decision.
- A residual between 1e-9 and 0.01 is explicitly incomplete for metrics requiring a unit-total portfolio, even if consistent with source rounding.
- Unsupported positions, negative weights, missing required portfolio sections, or ambiguous denominator definitions prevent an eligible analytical snapshot. Preserve evidence and return the reason.
- A snapshot can be source-complete but have partial identity/classification coverage or a residual. Each dimension is reported separately.

### Exposures and concentration

For each taxonomy node, exposure is the sum of analytical weights assigned to it. Cash and Unclassified are explicit nodes.

Node weights must sum to W within 1e-9, not forcibly to 1.0. Country totals and sector totals each conserve that same W. Classification coverage is the share of non-cash analytical weight assigned to reviewed nodes; return null when there is no non-cash weight.

Concentration consists of the top ten reported non-cash instruments after aggregating their position rows, and their aggregate analytical weight. Use instrument_id as a deterministic tie-breaker and retain all contributing source references. Do not infer issuer-level concentration until issuer mapping has its own contract.

### Overlap and active share

Aggregate supported positions by mapped instrument_id before calculating.

observed_overlap(F, G) = sum of min(wF_i, wG_i) over confidently matched instruments, including explicit USD cash under the declared convention.

Return full overlap and active share only when both portfolios are source-complete, have comparable denominators, fully resolved identities, nonnegative weights, and W = 1 within 1e-9:

active_share(F, G) = 0.5 * sum(abs(wF_i - wG_i))

Assert active_share equals 1 - overlap within 1e-9 for that eligibility domain. The comparison is against a selected peer fund; it does not claim to be against an official benchmark index.

Otherwise return observed_overlap as known matched weight, unresolved weight, totals, and eligibility reasons; active_share is null. Do not label it a full-portfolio overlap percentage or assert the active-share identity. Known matched weight is only a lower bound on same-basis matched reported weights, not a claim about an unknown true portfolio.

Crowding, when shown, reports the number of selected funds with a positive identified position and the sum of their weights. Label that sum “sum of fund weights”; it is not an AUM-weighted market ownership measure.

### Reported holdings changes

Compare two complete eligible snapshots using the same pinned identity mapping:

- new: absent or zero to positive;
- exit: positive to absent or zero;
- change: positive at both endpoints and abs(weight_to - weight_from) >= threshold;
- none: all other comparable cases.

Both endpoints must use the same analytical weight basis and compatible denominator definitions. If that contract changed, suppress activity events and report weight_basis_changed; a denominator change is not a portfolio activity signal.

Use source decimal precision for threshold comparison so a difference mathematically equal to 0.03 qualifies. The default threshold is 0.03, meaning three percentage points. New and exit events are not suppressed by that threshold.

Show both actual portfolio dates and the interval. A multi-day comparison is not labeled daily. Scheduled daily changes require both expected adjacent publication dates; otherwise display a coverage gap and suppress daily activity claims.

Corrections to an existing as-of snapshot generate a correction notice and invalidate current derived views. They do not become new manager-activity alerts.

Weight changes can reflect price movement, flows, corporate actions, reporting changes, or transactions. The MVP does not infer trades or automatically describe a fund as buying or selling.

## 9. Publication, replay, and freshness

### Atomic publication

Use one logical publisher enforced by a PostgreSQL advisory lock. Upload immutable source and canonical Parquet objects first. Verify hashes and schemas before attempting publication.

In one database transaction, publish the manifest, accepted snapshot memberships, mapping versions, and current-version pointer. A failed transaction exposes none of the candidate analytical state.

data_version is the SHA-256 digest of the canonical, sorted manifest content. Parent version, commit/run timestamps, and the current pointer are catalog metadata excluded from that hash. The catalog records when a version first became queryable. Publication time is not part of canonical analytical file content.

Readers resolve the current pointer once at query start and pin that manifest. They never assemble a dataset by listing every object under a directory.

The same canonical payload is an idempotent publication; it does not create another logical version or reset its first-publication time. A change to the pointer alone is not a new dataset. Objects left by failed publication are invisible to readers and may be garbage-collected only after a documented retention check.

### Rebuild and replay

The rebuild input bundle includes exact bronze bytes, original observation metadata, parser/schema versions, identity and taxonomy mappings, adapter configuration, code/methodology version, and recorded writer settings/dependency versions.

Replay writes to an isolated target and compares canonical sorted records and analytical outputs against the pinned input manifest. Operational run IDs and execution timestamps are excluded from semantic equivalence. Restoring the original stored artifacts must verify the original manifest and object hashes.

Byte-identical regenerated Parquet is not required. Because data_version covers physical object hashes, a rebuild with different Parquet bytes produces a different candidate data_version even when canonical records are equal; the comparison report records semantic equivalence and both versions. Such a rebuild does not automatically publish a new version. Exporting the exact stored artifact preserves its original bytes and checksum. A parser or mapping upgrade also produces a versioned comparison report.

Local storage and a temporary PostgreSQL database implement the same publication contract for development. A pure engine receives already loaded data and never discovers a current version itself.

### Freshness and run behavior

Track expected publication per fund, source, portfolio date, and source-calendar version.

Distinguish fresh, delayed_source, fetch_failed, parse_failed, quality_failed, unsupported, and unavailable. A successful file for one fund does not make another fund fresh.

An older accepted snapshot remains queryable with its actual date and stale status. Exact-date queries fail explicitly for missing funds; exploratory latest mode may return a clearly labeled partial basket.

Deduplicate storage by content hash, but retain distinct observations. Identical bytes do not prove publication for a newer portfolio date.

Scheduled runs have bounded retries, a maximum duration, and a work key that includes fund, source, and expected date, with distinct attempt records. This key identifies scheduled work, not an immutable source revision: a failed attempt may retry, and a later corrected file must still be observed and processed. Revision ingestion deduplicates using fund, source date, source-revision identity, and content hash.

Briefs pin their query inputs and report every basket member, including missing funds. Their logical key includes tenant, basket version, requested portfolio dates, and pinned report revision. Ordinary reruns reuse the same persisted brief; a correction creates a distinct report revision.

For email, persist an outbox record before sending and use a provider idempotency key where available. Do not claim exactly-once external delivery without provider support; uncertain delivery is marked unknown for reconciliation rather than retried blindly.

## 10. API, UI, and tenant boundaries

### Query contract

Use a discriminated Pydantic schema with unknown fields forbidden. Analysis values are exposures, overlap, concentration, holdings, and holding_changes. Crowding may be an overlap-result field.

~~~json
{
  "spec_version": "1.1",
  "universe": {"fund_ids": ["fund_example"]},
  "analysis": "exposures",
  "asof_date": "2026-10-30",
  "known_by": "2026-11-01T08:00:00Z",
  "data_version": "latest",
  "reference_mode": "as_known",
  "taxonomy": {"id": "pilot-sector", "version": 1},
  "freshness": "exact_date",
  "output": {"limit": 500}
}
~~~

The example fund ID is a placeholder, not a live fund. “latest” resolves once to the current immutable manifest and is echoed as its actual ID. As specified in section 6, that manifest retains earlier revisions and reference versions; readers select only versions eligible at the requested knowledge cutoff. A manifest's newer commit time does not make its later member revisions eligible. A saved result stores the resolved query and every selected reference version.

reference_known_by is required only when reference_mode is restated and is rejected in as_known mode. Resolve the latest eligible identity-mapping version at the applicable reference cutoff once per query and echo its immutable version. Explicit taxonomy versions must satisfy the same reference cutoff.

holding_changes requires from_date, to_date, and threshold; to_date must be later than from_date. overlap accepts two or more fund IDs and a documented basket-size limit of 25. Other requests reject fields belonging only to another analysis type. Taxonomy-dependent analyses require an explicit mapping version.

Endpoints:

- POST /v1/query
- GET /v1/funds and GET /v1/funds/{id}/coverage
- GET /v1/provenance/{id}
- GET/POST /v1/baskets and GET/PATCH/DELETE /v1/baskets/{id}
- GET /v1/briefs and GET /v1/briefs/{id}, introduced with M15
- tenant-owner administration for that tenant's membership and credentials
- separate minimal liveness and readiness endpoints

Every query result includes resolved query/spec hash, data_version, selected snapshot IDs and actual dates, knowledge/reference cutoffs, identity/taxonomy/methodology versions, weight basis, quality status, coverage, reasons for suppressed metrics, and provenance references.

Provenance links identify source rows and transformations. Provenance retrieval repeats authorization and source-rights checks; possession of an ID is not authorization. Document downloads are allowed only when source permissions allow them.

### UI

Use fixed server-rendered components for basket selection, coverage, exposure table/chart, overlap matrix, holdings comparison, and daily brief. Every financial result exposes provenance. Display stale/partial status adjacent to the relevant numbers.

Jinja autoescape stays enabled. Never render issuer or source text as trusted HTML. Provide keyboard navigation, visible focus, semantic tables, and WCAG AA contrast.

### Authentication and isolation

- OIDC authorization-code flow uses state, nonce, PKCE, and issuer/audience/signature/expiry validation through a maintained library.
- Tenant membership comes from server-side records. Do not infer it from an email domain, an unverified token claim, or a browser-supplied tenant ID.
- Use opaque server-side sessions and rotate the session at login; cookies are Secure, HttpOnly, and SameSite with a documented lifetime. Apply CSRF protection to cookie-authenticated mutations and revoke sessions on membership removal.
- API keys have scopes, expiry and revocation, are displayed once, and are stored only as a secure hash with a non-secret lookup prefix.
- Roles are owner and analyst. Only owners manage membership, credentials, and scheduled destinations.
- Shared source and taxonomy administration uses an audited platform-operator CLI and dedicated service role. Tenant owners cannot publish shared mappings or alter source configuration. The platform-operator role is distinct from tenant ownership and is not granted through the customer UI.
- Public source datasets may be shared only within their permitted audience. Baskets, memberships, credentials, briefs, saved queries, and audit logs are tenant-owned.
- Enforce RLS with a runtime role that neither owns tables nor bypasses RLS. Set tenant context transaction-locally and verify reset behavior with connection pooling.
- Tenant-derived artifacts use tenant-scoped catalog entries and storage keys. Any future cache key includes tenant and authorization scope; authorization is checked before a cache hit is returned.
- Use a local-only auth adapter for offline development. Startup must reject it in a deployed mode or on a non-loopback listener. Integration tests prove this restriction.
- External pilot access requires real OIDC configuration and successful login/logout/revocation checks.

## 11. Development, CI, and coding rules

Each cloud task already has an isolated environment. Use the existing checkout; do not create a Git worktree unless explicitly requested.

Root commands after the relevant tickets land:

- make setup: install pinned dependencies with uv sync --frozen; prepare documented local prerequisites.
- make check: lint, strict typing, import boundaries, and offline unit/property tests.
- make golden: executed financial fixtures for the implemented MVP methods.
- make integration: temporary/local PostgreSQL publication, RLS, API, and failure-path tests.
- make rebuild-fixture: run ingest.rebuild from pinned local fixture inputs into an isolated local target.
- make serve: launch the local authenticated-development workflow on loopback.
- make ingest-once: run the configured bounded source job; live sources require explicit runtime configuration.

Do not claim a command works before its implementation ticket and execution. README and any saved cloud startup instructions must match verified commands.

Use ruff, mypy --strict for ledger and engines, pytest, and hypothesis where generated cases test real invariants. Review dependency additions and commit the lockfile. List direct runtime and development dependencies in a documented allowlist; include Jinja2/Authlib and database tooling when introduced.

Pull-request CI is offline and uses fixtures. It runs applicable unit, golden, integration, secret-scanning, and boundary checks. A separate explicitly enabled integration workflow exercises real sources and managed authentication with scoped credentials and spend limits. Never convert a skipped live test into a readiness claim.

Rules for implementation:

1. Work one dependency-ready ticket at a time. State the approach and assumptions, then produce a reviewable change.
2. Use tests first for financial methods, snapshot selection, authorization, and other substantive behavior. Do not create trivial failing tests for documentation or scaffolding.
3. Prefer small cohesive PRs. Roughly 400 changed implementation lines is a review target, not a hard limit; fixtures, documentation, generated schemas, migrations, and bootstrap work are explicit exceptions.
4. A coherent contract change may touch multiple packages. Preserve import boundaries and describe the reason.
5. Existing golden expectations cannot change to accommodate implementation. A demonstrated error requires a separately reviewed methodology correction; newly specified edge tests are allowed in normal tickets.
6. Stop for unresolved financial meaning, rights, missing credentials, or destructive/external actions. Resolve routine implementation choices within these contracts and document them.
7. Do not log secrets, full authorization headers, or session tokens. Treat ingested text as untrusted data.
8. Do not deploy, apply Terraform, publish the cloud environment, or send external emails merely because an implementation ticket passed.
9. Nikhil's review/merge is the code gate. Merging does not automatically apply infrastructure or promote a release.

The scaffold writes concise AGENTS.md instructions reflecting this section; do not copy conflicting instructions from v1.0.

## 12. Financial fixtures and acceptance evidence

Preserve every input and expected numeric value from v1.0 section 13 in the versioned golden fixture. Use all six listed rows, including E and Cash.

Required MVP golden assertions:

- Original sector and country exposure tables.
- Fund1/Bench overlap 0.80 and active share 0.20 by both identities.
- Fund1/Fund2 overlap 0.65.
- Original crowding counts and aggregate weights.
- Original six change events at threshold 0.03.

Retain the attribution block unchanged as a deferred reference. A fixture loader checks it is present, but an unimplemented attribution engine is not represented as tested or as an expected failure.

New mandatory cases:

1. A position omitted from the next complete snapshot disappears.
2. A restatement removes an erroneous position; an earlier knowledge cutoff still returns the earlier revision.
3. Two same-day revisions are ordered correctly; identical portfolio dates do not collapse knowledge history.
4. A partial file or a crashed publication cannot replace the accepted snapshot.
5. Concurrent publisher attempts yield one serialized, complete history; readers never mix related inputs.
6. A backfilled document is unavailable before its observation/publication time.
7. Newer identity/classification knowledge does not leak into an as-known query; restated mode is explicitly labeled.
8. A 0.005 residual is visible, never assigned to cash, and suppresses active share.
9. Unknown sector preserves weight in Unclassified; exposure totals equal W.
10. Provisional identities do not create false cross-source overlap; resolving one does not create activity events.
11. Negative weights, derivatives, incompatible denominators, and missing weight fields produce explicit ineligibility.
12. A missing file for one fund is not cured by another fund's success.
13. Exactly 0.03 change triggers the threshold; a smaller change does not. New/exit precedence remains intact.
14. A correction generates a correction notice rather than an ordinary activity alert.
15. Replaying pinned inputs reproduces canonical records/results; publishing an identical artifact manifest is idempotent, and a semantically equivalent rebuild with different artifact hashes remains an isolated candidate.
16. Cross-tenant requests, object/provenance IDs, pooled connections, and revoked credentials fail safely.
17. A daily brief includes delayed/unavailable funds and cannot silently claim complete coverage.
18. When email is enabled, a crash around a send attempt produces the documented delivery state without an unqualified exactly-once claim. The persisted web brief is required even when email is disabled.
19. A query using the current manifest and an earlier cutoff remains correct after both holdings and mapping corrections.
20. A later source correction is ingested even after the scheduled job already succeeded for that fund/date.
21. Tenant owners cannot change shared source or mapping configuration.
22. Money-market fund units and explicit cash retain distinct asset categories and instrument identities through canonical and Arrow round trips. Different share classes remain distinct; reported precision and negative candidate evidence survive unchanged. Source classification does not itself approve a fund, identity mapping or metric.

Validate financial numbers deterministically. User research feedback and source-health observations are separate evidence from passing unit tests.

## 13. Dependency-ordered implementation tickets

Each ticket has a narrow outcome, dependencies, and acceptance evidence. “Complete” means applicable checks executed and the change reviewed; an external gate remains visible until independently verified.

| ID | Outcome | Depends on | Acceptance |
| --- | --- | --- | --- |
| M00 | Source feasibility and exact launch roster | none | Document authoritative endpoints, rights status, weight bases, fund calendars, required source fields, and at least two permitted dated samples from the first source. Establish daily three-year/since-inception historical feasibility for every proposed launch fund through coverage inventories, representative historical samples, revision semantics, delivery/use conditions and costs before adapter selection. Mark unresolved history and commercial-use requirements as blockers to the affected milestone. |
| M01 | Python scaffold, offline checks, original fixture | this spec | Packages and boundary rules exist; original six-row fixture and all expected values are preserved in one bootstrap PR; fixture loader/checks execute. No financial engine is claimed complete. |
| M02 | Core typed schemas, canonical hashes, quality contracts | M01 | Round trips preserve types; missing identities/dates/weights fail; canonical order is stable; source-completeness and metric-eligibility states are distinct. |
| M03 | PostgreSQL catalog, application schema, migration and role foundation | M02 | Migrations work from empty DB; rollback/failure paths tested; tenant RLS proven with runtime roles; local DB instructions verified. |
| M04 | First-source bronze fetch and recorded fixtures | M00, M02 | Recorded fetch handles dedupe, size/time limits, approved redirects, malformed responses, observation metadata, and source dates. Live capture is a separately recorded integration result. |
| M05 | First-source parser and snapshot quality assessment | M04 | Full fixtures parse; row provenance survives; missing sections/schema drift fail; weight basis/residual/unsupported-instrument cases follow section 8. |
| M06 | Instrument mappings, review queue, reviewed sector/domicile mappings | M03, M05 | Ambiguities remain provisional; mapping versions are immutable; review actions are auditable; identity and classification coverage are independently measured. |
| M07 | Atomic snapshot publication and point-in-time readers | M03, M05, M06 | Snapshot replacement, amendments, same-day revisions, concurrency, crash safety, and knowledge-cutoff cases pass. |
| M08 | Fixture rebuild and pinned replay | M07 | ingest.rebuild verifies the original artifact manifest and reproduces canonical records/results from the pinned bundle; changed artifact hashes or parser/mapping versions produce a versioned difference report. |
| M09 | Exposure, concentration, overlap and crowding engines | M02, M06 | Applicable original golden numbers pass; non-unit totals preserve W; eligibility and null active-share cases pass; engines perform no I/O. |
| M10 | Holdings changes and correction-event behavior | M07, M09 | Original alert events and all threshold, omission, mapping-change, correction, and gap cases pass. |
| M11 | Per-fund scheduler, freshness and operations records | M08, M10 | Bounded replayable jobs; holiday/deadline cases; no issuer-wide false freshness; missing fund remains visible. |
| M12 | Managed OIDC adapter, local auth, API keys and tenant membership | M03 | Offline auth/session/CSRF/revocation tests; deployment rejects local auth; cross-tenant and pooled-session tests pass. Live Cognito smoke remains a separate gate. |
| M13 | Typed query API and authorized provenance | M07, M09, M10, M12 | Valid queries reproduce goldens; invalid/unsupported queries fail; versions resolve and pin once; all object-level authorization cases pass. |
| M14 | Minimal basket and analysis UI | M11, M13 | A user can inspect coverage, exposures, overlap, and changes with provenance; partial/stale results are clear; keyboard/escaping checks pass. |
| M15 | Deterministic daily brief; optional email adapter/outbox | M11, M13 | Brief includes all basket members and gaps; fixed templates reflect table values; persisted-brief rerun tests pass. Outbox/crash checks apply if email is enabled; external sending stays off until configured and authorized. |
| M16 | Optional second issuer | M00, M08, M11 | New adapter meets the same source, rights, schema, completeness and calendar contracts; existing issuer results do not regress. |
| M17 | Pilot hardening, costed deployment plan and recovery rehearsal | M08, M12–M15; M16 if included | Representative benchmark; backup/restore in isolated target; rights/coverage review including full historical backfill reconciliation; security tests; pinned artifact and manual deployment instructions; budget reviewed. |
| M18 | Explicitly authorized pilot deployment and customer validation | M17 plus external prerequisites | Actual login/revocation and source checks pass; ten funds covered for five expected days; user workflow reviewed; costs observed; deployment/rollback evidence recorded. |

M01–M03 can progress while source permissions are investigated, using synthetic fixtures. M09 can start after its own dependencies while publication work continues. M12 can proceed after M03. Other parallel work must respect the listed prerequisites.

M00 does not require inventing reference data or live credentials. If a source is unsuitable, document the finding and propose a replacement roster before claiming source coverage.

## 14. Release and operating gates

### Local development ready

Pinned installation, offline checks, golden calculations, temporary-Postgres integration tests, fixture rebuild, and the local UI/API workflow have all executed successfully. Save reusable cloud installation/start instructions only after the corresponding commands have been tested. Preserve existing environment settings and use the supported configuration workflow.

### Data pilot ready

Source usage has been reviewed; ten named funds meet the scope; relevant per-fund publications pass for five expected days; manual inspection of representative snapshots and changes agrees with source evidence. Missing/unresolved weights are reported by weight as well as row count.

Every launch fund's full daily historical backfill meets the three-year/since-inception minimum and has been reconciled against its approved fund/date inventory and calendar. Missing expected dates, rejected snapshots, unsupported positions, revision limitations and metric eligibility are visible separately; no synthetic dates or normalized weights repair coverage. Retained artifacts and provenance support replay under the agreed use and retention conditions.

### External pilot ready

Real authentication is verified; tenant isolation tests pass; backup restoration succeeds; hosted latency and recurring cost estimates are recorded; Nikhil has explicitly authorized deployment and any outbound delivery. Source restrictions govern which data is displayed/exported.

### Recovery and retention

Document S3 versioning/retention, database backup and point-in-time restore settings, and an isolated restore procedure. Restore the catalog and referenced objects together; a restored current pointer must never reference missing objects.

Retain immutable manifests, analytical artifacts, source evidence, and applicable engine versions for the pilot's agreed retention period. Define that period with source rights and customer terms before external launch; do not promise indefinite storage or executable replay without it.

Audit records include actor, tenant, action, resolved query/version references, authorization outcome, and time. Runtime roles cannot alter audit history. Record deletion/retention policy separately from immutable analytical history.

## 15. Expansion roadmap and prerequisites

| Expansion | Prerequisite |
| --- | --- |
| More US ETFs | Adapter reliability, coverage metrics, per-source permissions, and operational budget demonstrated |
| N-PORT and broader asset classes | Current official filing/publication rules verified; appropriate liabilities, derivatives, identifier, and snapshot contracts |
| Licensed data feed | Explicit source/reference-data redistribution rights, export enforcement, historical coverage and revision guarantees |
| Custom taxonomies | Tenant-private mapping lifecycle, authorization of derived data, review workflow and clear historical semantics |
| AI classification or natural-language queries | Verified provider APIs/costs; held-out calibration; deterministic numeric validation; abstention and evidence checks |
| Attribution and factors | Licensed benchmark/return inputs, currency/total-return conventions, attribution residual policy, risk-free returns and reviewed formulas |
| Names Rule workflow | Secure current-client-holdings input, qualified methodology review, eligibility/denominator/derivative rules, monitoring and exception handling, evidence approval workflow |
| Enterprise platform controls | Contract-driven SSO/residency/retention needs, security assessment and appropriately scoped compliance programme |
| Redis, gold tables, larger query infrastructure | Measured bottleneck and a design preserving version, tenant and authorization boundaries |

The original Brinson–Fachler golden expectations remain available for the attribution expansion. The original spec's API availability, pricing, regulatory statements, broad source coverage, and compressed-storage sizing require current verification before use.

## 16. Decisions to record before their dependent milestone

| Decision | Owner/action | Needed by |
| --- | --- | --- |
| Exact eligible fund roster and issuer endpoints | Source investigation with Nikhil review | M04 live integration |
| Source, reference-data, display and retention rights | Nikhil obtains appropriate terms/review | Data/external pilot |
| Sector vocabulary and reviewed mappings | Nikhil reviews documented taxonomy and evidence | Customer-facing exposures |
| Real cloud/identity configuration and secure credentials | Nikhil configures settings; implementation verifies bindings | M18 |
| Customer audience and value test | Nikhil selects initial user and reviews feedback | Pilot sign-off |
| Costed hosting plan and retention period | Nikhil reviews measured/quoted costs and applicable terms | M18 |
| Email provider and recipient authorization | Configure only if email is part of the pilot | First external delivery |

Missing external prerequisites do not block independent synthetic development. They do block claims that the affected live workflow is ready.
