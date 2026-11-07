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

## 1 November 2026 — M02 candidate data contracts

Merged through PR #1 into main at c6bbce2. The
[data-contract reference](data-contracts.md) documents schema 1.0.0 and canonical
hash format fund-ledger-records-v1.

- Added frozen source-document, snapshot, position and instrument models.
- Kept source completeness, identity/classification coverage, disposition and
  reasons separate; preserved signed/unsupported candidate evidence for later
  ingestion checks.
- Added explicit Arrow schemas and lossless in-memory round trips.
- Added order-independent canonical record hashes with duplicate-key rejection,
  record-kind/version separation and source-precision preservation.
- Added Pydantic, PyArrow and Hypothesis with allowlist reasons and an updated
  lockfile. No existing golden values or financial engine versions changed.

Tests were written first and failed because the new modules did not exist.
Further failing regressions exposed decimal exponent-casing dependence and
UTC normalization overflow; both were corrected and rechecked.

Final local validation: make check passed (112 tests, strict typing, formatting,
four import contracts and dependency checks); make golden passed (9 fixture
checks included in those 112); git diff --check passed. The original source
archive checksum remains unchanged. No live issuer, database, or hosted CI
validation is claimed by these results.

At implementation time, creating the PR through the GitHub CLI was blocked by
the runtime's api.github.com policy. The user subsequently created and merged
PR #1. The pending domain addition in the environment draft does not establish
runtime API access; the issuer access limitations remain recorded in sources.md.

## 1 November 2026 — M03 PostgreSQL foundation

Merged through PR #2 into main at d655c3c after implementation on
feat/m03-postgres-foundation. The [database guide](database.md) records the
local commands, schema, role grants, and integration setup.

### Approach and scope

- Use PostgreSQL 17 and packaged Alembic revisions. Keep administrative role
  bootstrap separate from transactional schema changes, and require an explicit
  database name for every migration API call.
- Separate NOLOGIN owner, runtime, and publisher groups. Reject unsafe existing
  group roles instead of silently accepting or downgrading their privileges.
  Application logins are provisioned separately and never receive owner rights.
- Store dataset manifests, append-only catalog history under publisher grants,
  and a singleton current pointer. Parent references and the current pointer
  require an existing catalog commit. M07 owns atomic publication, concurrency,
  knowledge-cutoff semantics, and point-in-time readers.
- Add tenant, membership, basket, and audit tables. Force RLS on every tenant
  table, check both visible and written tenant IDs, and deny rows when context
  is absent. Runtime grants make membership/tenant rows read-only and audit rows
  append-only; basket writes remain tenant-scoped.
- Scope each pooled request to a transaction-local UUID supplied by the trusted
  backend, clear stale session context before and after use, and reject unsafe
  connection roles. M12 must authenticate callers and authorize membership
  before selecting this UUID.
- Run a repository-labelled Docker container through the local Unix socket,
  pinned by image digest, bound to loopback, and backed by disposable tmpfs.
  Local trust authentication contains no real credentials and is intended only
  for this isolated development/test service.
- Keep offline checks independent of PostgreSQL. A separate integration command
  and CI job use real restricted logins and unique temporary databases. The
  fixture rejects remote targets and removes only resources it allocated.

### Verification record

Migration and permission tests were written first. The initial missing-module
failure established the baseline; later failing regressions exposed implicit
database selection, an uncommitted catalog parent, and privileged pool
connections. These behaviors received explicit guards or constraints.

Local validation after the security fixes:

| Check | Result |
| --- | --- |
| Disposable service restart and make db-status | Passed SQL readiness on a fresh cluster |
| make db-migrate, repeated | Passed twice at 0001_foundation |
| make integration | Passed: 32 tests, including migration rollback/re-upgrade, tenant isolation, grants, pool reuse, and security regressions |
| make check | Passed: 112 offline tests, lock consistency, Ruff, strict typing, import boundaries, and dependency policy |
| Final connection-timeout adjustment | Integration suite, lint, and strict typing passed again |
| Hostile ambient PostgreSQL routing settings | Local migration helper retained its fixed loopback target |
| Ledger wheel build | Passed; packaged Alembic environment and revision files were present |

The original golden expectations remain unchanged. These are local results;
hosted CI remains a separate verification gate. Database startup guidance was
saved in the cloud environment configuration draft without publishing it;
the existing installation instructions were retained.

This ticket does not deploy a database service, publish the cloud environment,
implement authentication, or establish source-data coverage. No production
credentials, Terraform, application server, or financial engine is introduced.

## 6 November 2026 — M00 issuer register and importer plan

At Nikhil's request, official issuer downloads are the preferred source route.
The investigation sample now includes Capital Group, Avantis, Dimensional,
T. Rowe Price, Fidelity, and JPMorgan Asset Management. This extends research,
not the approved fund universe. Capital Group and Avantis remain first in the
investigation order; seed tickers are unverified discovery leads.

Added config/issuer_sources.json as the canonical research mapping and
docs/issuer-sources.csv as its spreadsheet export. The register separates
network access, usage permissions, sample evidence, field mappings, quality,
and source admission. Its guide defines scoped permission decisions linked to
specific terms clauses. No issuer is approved and no production import is
enabled. The small exporter regenerates/checks the CSV without network access.

The current runtime policy was rechecked and blocks all six discovery hosts.
No issuer HTTP request was retried against that policy; no terms document or
holdings file was obtained. Terms and quality assessment remain unperformed,
and M00 remains incomplete. The source mapping records these gaps explicitly.

The existing environment draft was preserved and four exact discovery domains
were added: www.dimensional.com, www.troweprice.com, www.fidelity.com, and
am.jpmorgan.com. Draft persistence was confirmed; runtime activation and
publication are user-controlled and have not been established by the save.

docs/importer-plan.md defines the next sequence: obtain source evidence and two
distinct dated samples; implement bounded M04 acquisition and immutable original
files; implement M05 parsing and candidate quality checks. Publication and
historical-as-known readers remain M07. No importer implementation or recurring
job is included in this change.

Local validation: make check passed, including 112 offline tests, strict typing,
format/lint, package boundaries, lock consistency, and dependency policy. The
CSV matches the JSON; six unique candidates, empty evidence collections,
disabled admission, documentation links, and spreadsheet formula escaping were
checked. git diff --check passed. The archived specification checksum and
golden expectations are unchanged. No database test rerun was needed for these
research/export changes; hosted CI and all live issuer checks remain unverified.

## 6 November 2026 — environment activation and first live issuer review

The user published a newer environment version. Its replacement runtime applies
the six issuer discovery hosts and api.github.com; all six homepages returned
HTTP success or same-host redirects through the configured proxy. The earlier
blocked network status is historical. The new draft lacked installation and
startup instructions, so the previously tested make setup/check script and
PostgreSQL startup guidance were restored. New published network settings,
repository selection, variables, credentials, and presets were preserved, with
no conflicting settings found. No environment publication was performed by the
agent. Frozen setup and all 112 offline tests passed in the replacement instance.

The [live assessment](issuer-assessment.md) records source-linked terms or policy
findings for the six issuers. Dimensional, T. Rowe Price, and Fidelity have
commercial/automated-use restrictions; JPMorgan has protected-content reuse and
storage conditions subject to stated exceptions. Capital Group's reviewed
third-party notices do not establish rights to its own holdings, and its linked
advisor composites route led to authentication. No credentials or consent gate
were used. These are preliminary evidence findings, not issuer permission or a
legal determination applying indiscriminately to every underlying fact.

Avantis's main terms grant a limited download licence. Three actual product pages
were inspected: AVUS, AVUV, and AVTM, each with holdings dated 5 November 2026.
Their embedded arrays contain 1,943, 793, and 1,709 rows respectively. Independent
Decimal sums reproduced displayed totals of 99.19%, 99.83%, and 98.95%. These
are raw all-row values, not admitted analytical W. Rounded-zero rows, sweep
vehicles, rights, and other position types require explicit scope and quality
review. No normalizing, balancing cash, new financial methodology, or source
admission was performed. No standalone CSV/XLSX or second portfolio date was
obtained. Source pages and constituent rows remain in private ignored cache;
Git stores only the research mapping, aggregate observations, and limited evidence.

An actual Avantis catalog link identifies quarterly holdings documents on
avantisinvestors.prospectus-express.com. That exact host was added to the saved
draft while preserving existing settings; it remains outside the current runtime
policy until user activation. No request to that host was made. The separately
observed factsheet host was not added because factsheets do not establish full
holdings. No wildcard or alternate route was introduced.

The mapping and importer plan now reflect actual source constraints. M00 remains
open for an approved roster, permissions, a complete source contract, and two
distinct dated samples. M04/M05 implementation and customer-facing source use
remain dependent on those requirements; no importer or scheduled job was added.

Final local checks passed after integration of the live findings: make check
(112 offline tests and required static checks), CSV regeneration/drift, unique
IDs and references, document/sample hashes and byte lengths, measurement
arithmetic, disabled admission, and local documentation links. Independent
review matched the quoted clauses to cached source bodies. The archived spec
and golden expectations remain unchanged; hosted CI has not been observed.

## 6 November 2026 — refine daily disclosures and factual-use assessment

The user asked to distinguish official daily disclosures and factual holdings
from proprietary additions, and to assess the actual access/reuse route rather
than infer a paid-licence requirement from general website terms. The research
mapping is now schema 1.2.0. It preserves the original 24 rights decisions and
adds 12 scoped superseding reviews, with explicit material scope, applicability,
use basis and separate production admission. No paid-licence requirement is
established by the reviewed evidence. Explicit website-access restrictions remain
recorded; factual-use reasoning does not authorize a restricted retrieval method.

Avantis's product-specific Definitions describe disclosure of each position every
business day before trading. The official AVUS All Holdings route was retrieved;
all 1,943 rows and fields match the earlier product capture. Static inspection of
the issuer's download control verifies a client-side CSV export from the same
array, with no extra weight precision; no browser-generated CSV was captured.
The separate Daily Pricing Basket uses different data and cannot substitute for
portfolio holdings. Issuer-declared coverage is now recorded separately from
independent reconciliation and numerical eligibility.

JPMorgan's public directory and product data verify JGRO and its fund-specific
Download All Holdings control. The endpoint returned a real 27,245-byte XLSX
with 140 positions and an internal 5 November 2026 date. Raw market-value weights
total 100.00%; raw net-assets weights total 100.06%. Negative USD cash value and
quantity round to zero in both weight columns. Money-market and ADR positions,
identity resolution and the denominator contract remain unresolved. Both bases
are preserved; neither is approved as analytical W. Workbook sector/industry/
country fields and protected presentation are separate from core factual data.

Five holdings observations now cover four funds, all on one portfolio date;
the additional AVUS capture does not count as a second date. There is one actual
standalone holdings file. No source admission, ten-fund roster, production
importer, scheduled job or financial-methodology change is included. Source
bodies, scripts, workbook bytes and constituent datasets remain in ignored private
review storage; Git contains limited findings, metadata and aggregate measures.

The importer plan now compares the verified JPMorgan XLSX and Avantis HTML/client
export routes, with field-specific use review and exact financial constraints.
Capital Group's public listing has an observed off-host search dependency but no
verified daily route. Existing restrictions/gates for other issuers remain scoped
to the reviewed routes; no authentication or consent was accepted or bypassed.

The environment draft adds www.ecfr.gov for current Rule 6c-11 verification,
preserving the previously proposed quarterly-documents host and all setup/start,
repository, preset and credential settings. Readback confirmed revision 4. The
host is not active, no regulatory request was made, and fund-specific reliance
on the rule is not asserted. No environment publication was performed.

Validation: make check passed (112 offline tests, lint/format, strict typing,
import boundaries, dependency allowlist and lock consistency). The CSV matches
the register. All 32 document/sample/discovery-evidence hash and byte records
match private captures. References, unique IDs, sample/date counts, disabled
admission, historical numeric measurements, local documentation links and
archived-spec checksum passed. Independent review reproduced the JGRO workbook
counts, two weight totals and negative-cash finding, and checked exact source
quotes. No database changes required an integration rerun; hosted CI is unobserved.

## 6 November 2026 — JPMorgan second-date, roster and source-contract validation

The user authorized continued source validation before M04. The new
[JPMorgan report](jpmorgan-source-validation.md) and
[structured validation](../config/jpmorgan_source_validation.json) record the
complete 31-fund active-equity subset of the official 78-ETF US directory.
Thirty new public product JSON requests supplemented cached JGRO data. Eight
options/ELN strategies, one short strategy and four additional funds holding
futures are excluded by current strategy/position rules. Eighteen remain scope
research candidates; all 31 contain money-market investments. Every International/
Global fund also has known non-USD cash. No fund is admitted under current scope.

Five candidates avoid observed derivative/short, negative-cash and non-USD-cash
issues: JAVA, JPEF, LGDS, LVDS and JPSV. Their money-market rows suggest two fund
instruments, but truncated descriptions and unverified source IDs do not establish
exact fund/share-class identities. REIT/ADR mappings remain necessary. Every
reported net-assets total in this set differs from one; current full-overlap and
active-share gates would still apply. This is not an approved ten-fund roster.

A separately reviewable proposal would support identified money-market fund units
as direct securities, retaining their identities/weights and treating them as
non-cash securities. It does not authorize look-through, matching different funds
as cash, signed-cash analytics, non-USD cash, derivatives, relaxed numerical rules
or a lower pilot fund count. The current specification/models/golden expectations
remain unchanged. The user must decide whether to change the supported-asset
scope or retain it and continue investigating other sources.

The JGRO workbook was re-fetched at 21:39:47 UTC and still reports 5 November. All
financial ZIP member contents are identical to the earlier sample; only document
properties and ZIP timestamps changed. The official historicalData response has
no populated holdings history or available dates. This is a new retrieval
observation, not a second portfolio date or financial revision. Register schema
1.3.0 adds that distinction and a source-validation reference. No recurring job,
speculative date URL or pricing-basket substitute was introduced.

The source contract proposes reported percent-of-net-assets as the primary basis
pending reconciliation, retaining market-value weights separately. Same-date
public NAV×shares agrees with the published assets reference within $0.015, but
holding-value ratios do not reproduce all reported weights under ordinary nearest
0.01-percentage-point rounding: 12 rows lie outside that assumed interval. The
issuer rounding algorithm and precise denominator semantics remain unverified.
No gap is assigned to cash, no weights are overwritten and no source error is
asserted. Exact publication calendar/deadline and negative-cash cause remain open.

The official prospectus link returned a wrapper for connect.rightprospectus.com.
That exact host was added to saved environment draft revision 5; readback verified
preserved setup/start instructions, repository and presets. It remains outside
active policy, so the prospectus content was not fetched. No environment was
published. No new paid-licence requirement was established; operation-specific
use and original-artifact retention remain separate review questions.

Validation passed: make check with 112 offline tests and required static checks;
CSV drift; 70 document/sample/evidence records against private hashes/byte lengths;
31 unique fund records,13 disjoint exclusions and the conditional five-fund set;
local links and unchanged archived-spec checksum. Independent review reparsed
the XLSX and reproduced both weight totals, the conditional rounding diagnostic
and metadata-only comparison, and checked source strategy quotes and roster
measurements. No raw constituent data or source files were committed. Database
integration was not rerun for this documentation/research update; hosted CI is
not claimed observed.

## 7 November 2026 — approved money-market category and second daily portfolio date

The user approved the narrow extension for identified money-market fund share
classes. The active specification now includes those direct positions separately
from Cash, preserving share-class identities, original values/weights and source
evidence. No look-through, cash equivalence, par assumption, broader pooled-fund
scope, negative-cash analytics, foreign-currency cash or derivative support was
added. Numeric/residual/full-overlap gates and the ten-fund target are unchanged.

AssetCategory.MONEY_MARKET_FUND is an additive candidate-record value. Four new
behavior tests failed first because that value was absent, then passed after
implementation. They cover distinct share classes/cash through JSON, Arrow and
canonical serialization, hash distinction when relabeled as cash, signed source
precision and required identity evidence/provisional keys. Existing physical
schema and canonical encoding/version remain unchanged, preserving old records'
hashes. Older readers explicitly reject the new enum value and must be upgraded
before consuming such records. No current database enum/column needs migration.
This is representation support, not an implemented financial engine or automatic
classification/source admission.

The user also asked why older daily history had not supplied a second date.
Both earlier checks occurred on 6 November and returned the current 5 November
portfolio; the checked holdings-history response exposed no prior dates. A fresh
7 November retrieval at 13:30:41 UTC now returns an internally dated 6 November
XLSX. Fresh product JSON independently matches its date, 140 positions and both
weight totals. The 17-column layout is unchanged. Market-value weights total
100.03%, net-assets weights 100.05%; no negative quantities or values occur on
this date. The 5 November negative-cash finding remains intact and date-specific.

We therefore have two actual prospectively captured daily source files, for
5 and 6 November, without claiming two accepted analytical snapshots. The fresh
history response contains 1,067 daily NAV/market-price observations from 9 August
2022 and 1,068 closing-price observations from 8 August 2022 through 6 November
2026. Historical holdings and available holdings dates remain null. Daily price
history is not constituent history; the bounded check does not prove earlier
daily portfolios are unavailable elsewhere. No archive date parameter, pricing
basket substitution, backdated observation or recurring job was introduced.

Register schema 1.4.0 and source-validation schema 1.1.0 record the scope approval,
new sample, date-specific findings and remaining identity/use/denominator gates.
All source/fund production flags remain disabled. The 31-fund screen remains a
5 November cohort; its five structural candidates have not been reclassified or
admitted merely because the new asset category exists. Spreadsheet measurements
now include portfolio dates to distinguish the two JGRO observations.

Validation passed: make check with 116 offline tests and required static checks;
77 provenance records matched private captures; IDs, counts, CSV drift, local
links and disabled admission were verified. Independent review reparsed the new
workbook, checked price-history ranges and confirmed unchanged prior numeric
samples, original archive/goldens and old canonical hash behavior. No database
integration rerun was needed for the additive record category. Hosted CI remains
unobserved. No source files/constituent datasets were committed and no environment
configuration was changed or published in this turn.

## 7 November 2026 — historical sourcing before importer selection

The user prioritized credible historical sources and explicitly selected daily
holdings for at least three years, or since inception for newer ETFs. The active
specification now requires that history for each launch fund, anchored to its
latest expected portfolio date and verified calendar. M00 must establish
feasibility through a complete fund/date inventory and representative historical
files before selecting an adapter. Full acquisition and reconciliation follow
implementation and are required before pilot sign-off. Two recent JGRO files
remain valid format evidence but do not establish a historical archive.

The historical-source assessment and version 1.0.0 candidate mapping record seven
research candidates: JPMorgan and Avantis archive delivery, ETF Global, FactSet,
Morningstar, Intrinio, and SEC filings as periodic comparisons. Commercial names
and public starting URLs are research leads from general knowledge; no current
product claims, daily coverage, prices or use conditions were live verified.
All historical coverage/quote fields remain unknown and production is disabled.
The earlier issuer evidence is referenced, not replaced. The proposed investigation
requests a full date inventory, separated older files and a 20-date consecutive
window; this sampling plan is not proof of continuous coverage by itself.

Historical acquisition preserves actual observation time, original reported
weights, portfolio and revision identity, and unsupported rows. Neither periodic
filings nor price/NAV history may substitute for daily holdings. Vendor backfill
plus direct issuer acquisition is a candidate design requiring same-date
compatibility evidence. Today's fund roster is not a survivorship-free historical
universe. The whole-platform recurring cost target remains below US$1,500/month;
no provider contact, purchase, agreement or feed implementation was authorized.

The enforced runtime policy still excludes the commercial/SEC research hosts.
Environment draft revision 7 adds www.sec.gov, www.etfg.com, www.factset.com,
developer.factset.com, www.morningstar.com, intrinio.com and docs.intrinio.com.
Readback confirmed all prior hosts, presets, setup/start instructions and
repository settings were preserved. The save response requires publication;
user review/save/publication remains pending. No excluded host was requested,
no network restriction was bypassed and the environment was not published.
Live product verification and actual historical samples remain outstanding.

Validation passed: make check with 116 offline tests and all required static
checks; candidate IDs, existing sample references, null coverage/quote fields,
disabled admission, local links, unchanged issuer CSV and archived-spec checksum.
Independent review found no unsupported vendor claims or archive/admission
conflation; an obsolete initial-investigation instruction was clarified.
No application code or original golden data changed; database integration was
not rerun for this documentation/mapping update. Hosted CI remains unobserved.
