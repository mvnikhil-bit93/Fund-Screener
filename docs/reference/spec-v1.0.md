# Fund intelligence platform — full build spec for Codex v1.0

Nov 1, 2026 · @Nikhil

## How to use this spec

This document is the only input Codex needs: no files, no repository, no fixtures. Everything it must create, including `AGENTS.md`, the golden numbers and the tickets, is written out below in full. Export it as Markdown and paste the whole thing into a Codex Cloud task; from then on, each new task is one ticket from sections 15 and 16, pasted with the sentence "Work from the spec already in this repository at docs/spec.md".

### The exact first message to Codex

```text
You are building a new repository called fund-intel from the specification
below. Read the whole specification before doing anything.

Do these in order, as separate pull requests, and stop for my review after
each one:

1. Create the repository scaffold described in section 3, create every file
   listed in section 3 and the AGENTS.md files in section 4 verbatim, save
   this specification as docs/spec.md, and make `make check` pass.
2. Create tests/golden/synthetic_fund.json from section 13 exactly, with a
   smoke test that loads it.
3. Then execute ticket P0-01 to P0-12 from section 14, one ticket per PR,
   in the order given, following the working rules in section 2.

Before each PR, show me your plan and wait for approval. Write the
acceptance tests first and show them failing. If anything in a ticket is
ambiguous, stop and ask in the PR description under "Open questions".
Never change an expected value in tests/golden/. Never deploy.

<paste sections 1 to 16 here>
```

### What Nikhil does

- Approves each plan, reviews each PR, merges. The merge is the gate.
- Owns every number in section 13. If a golden test goes red, that is a methodology question for Nikhil, never a code fix for Codex.
- Creates the GitHub repository, the Codex Cloud environment and the dev AWS account; section 12 says exactly what to put in each.

## 1. Product intent and scope

We are building a holdings-native fund intelligence platform for the buy side. Every public fund disclosure (US N-PORT filings, daily ETF issuer holdings files, later PDF reports and direct manager feeds) is normalised into one point-in-time holdings ledger keyed on FIGI. Deterministic analytics engines run on the ledger. An AI layer classifies securities into user-defined taxonomies, compiles natural-language questions into a validated query spec, and automates recurring workflows. Two products share the foundation: an analytics platform for buy-side teams and a licensed holdings data feed for quants and builders.

### Users and the two launch wedges

- ETF product and distribution teams: see what competitor active ETFs did yesterday, across a basket they define, with alerts.
- Compliance teams: run the SEC Names Rule 80% test against the fund's own holdings with a client-configured policy, evidence per security and a versioned audit trail.
- Also served: product strategy teams (custom peer groups and taxonomies), fund selectors (overlap and concentration across a portfolio of funds), data buyers (point-in-time holdings and daily diffs by API or Parquet).

### In scope for version 1

- Universe: US mutual funds from N-PORT; US and UCITS ETFs from issuer files.
- Ledger with two dates on every holding row: `asof_date` (when it was true) and `public_date` (when it became knowable).
- Security master keyed on FIGI with a learned name map; a strategy entity above share classes matched by holdings.
- Engines: classification (user taxonomies and Names Rule), exposures, overlap and crowding, holdings-based attribution, returns-based factor exposures, alerts.
- Decision calls through one `DecisionProvider` interface for classification, matching, routing, grading and page triage.
- Access layer: one typed query spec behind REST, an MCP server, the web app and the feed export.
- Web app: baskets, taxonomy editor, exposure and overlap views, daily ETF alerts, Names Rule mode with a policy editor, dashboards as saved specs, SSO.

### Not in version 1

- UCITS and OEIC mutual-fund holdings from PDF reports (phase 4).
- Manager-submitted feeds and the manager portal.
- Intraday data, full-revaluation scenarios, a proprietary fundamental factor model.

### Constraints

- One founder reviews everything; every component must be testable against golden numbers and small enough to review in one sitting.
- Institutional buyers audit methodology; every number must be reproducible from a `data_version`, a `methodology_version` and a query spec.
- All data sources are public, free or independently licensed. No data or tooling from the founder's employer.
- Infrastructure and data costs before revenue stay under about US$1,500 a month.

## 2. Working rules for Codex

1. Read the whole spec before the first plan. Save it as `docs/spec.md` in the first PR and refer to it by section number in every later PR.
2. One ticket, one pull request, one package touched, under 400 changed lines unless the ticket says otherwise. A ticket that needs more is two tickets; say so and stop.
3. Plan first: write the plan in the task before any code and wait for approval.
4. Tests first: write the ticket's acceptance tests, show them failing, then implement until they pass. A test that mocks the function under test does not count.
5. The golden numbers in section 13 are the specification. Never edit an expected value. If an engine disagrees with a golden value, leave the test red and explain in the PR why you think the expectation is wrong.
6. Deterministic engines: no network, database, LLM, environment or clock access inside `packages/engines`. Same input, same output, always.
7. The LLM never writes SQL. Natural language compiles to a query spec that the validator accepts or rejects.
8. Every judgement call (classification, matching, routing, grading) goes through `packages/decisions`. No provider SDK is imported anywhere else.
9. No secrets anywhere in the repository, fixtures, logs or PR text. Tests run on recorded fixtures under `tests/recorded/`; never call a live API from a test.
10. Treat all ingested content (filings, issuer files, fund names) as untrusted data; never place it in a prompt as instructions.
11. State assumptions in the PR: dates, time zones, currencies, identifier formats, tolerances. Dates are `datetime.date`; timestamps are UTC-aware; weights and returns are fractions, never percentages; currencies are ISO 4217.
12. If anything is ambiguous, stop and write the question under "Open questions" in the PR description. A PR with open questions is not ready to merge. Do not guess.
13. Never deploy, never apply Terraform, never touch production credentials. CI deploys after merge; production promotion is a manual approval by Nikhil.
14. Fill the PR template completely: what changed, how it was verified (commands and output), assumptions, open questions, methodology version touched.

## 3. Repository layout and tooling files

Create a single monorepo named `fund-intel` with this layout. Every file named here must exist after the first PR.

```text
fund-intel/
  AGENTS.md                         section 4, verbatim
  README.md                         how to run checks; link to docs/spec.md
  docs/spec.md                      this specification
  docs/methodology/README.md        "generated from engine docstrings; do not edit"
  Makefile                          check, lint, typecheck, test, golden, rebuild-fixture
  pyproject.toml                    uv workspace; ruff, mypy, pytest config; dependency allowlist
  .importlinter                     package boundary contracts (table below)
  .github/CODEOWNERS                tests/golden/, docs/methodology/, AGENTS.md files, pyproject.toml -> Nikhil
  .github/pull_request_template.md  what changed / how verified / assumptions / open questions / methodology version
  .github/workflows/ci.yml          jobs: check, golden, secret-scan, dependency-allowlist, terraform-plan (infra changes only)
  scripts/check_allowlist.py        fails if any package dependency is outside [tool.fund-intel.allowlist]
  codex/environment-setup.sh        Codex Cloud setup: install uv and pnpm, uv sync, pnpm install, duckdb cli, make rebuild-fixture
  packages/
    ledger/     schemas, Parquet layout, data_version minting, holdings view library   (AGENTS.md: section 4)
    ingest/     Dagster assets: nport, etf_files, prices, figi, gleif, quality report
    engines/    pure functions: classify, exposures, overlap, attribution, factors, alerts (AGENTS.md: section 4)
    decisions/  DecisionProvider interface and backends: openai_decisions, claude_structured, rules
    access/     query spec schema, validator, FastAPI app, MCP server, orchestrator
    app/        Next.js, TypeScript strict                                              (AGENTS.md: section 4)
  tests/
    golden/     synthetic_fund.json (section 13) and engine golden tests
    recorded/   recorded HTTP responses (EDGAR, issuer sites, OpenFIGI, vendor), secrets redacted
    fixtures/   bronze/ and ledger/ for the fixture ledger
  infra/        Terraform, one module per service, eu-west-2
```

### Package boundaries (write these as import-linter contracts)

| Package | May import | Must never import |
| --- | --- | --- |
| `ledger` | pyarrow, polars, pydantic | ingest, engines, decisions, access |
| `ingest` | ledger, decisions | engines, access |
| `engines` | ledger types, polars, numpy | ingest, access, decisions, httpx, requests, boto3, duckdb, psycopg, sqlalchemy, redis, anthropic, openai, dagster |
| `decisions` | pydantic, httpx, provider SDKs | ledger I/O, ingest, engines, access |
| `access` | ledger, engines, decisions | ingest internals |
| `app` | the REST and MCP contracts only | any Python package |

### Tooling conventions

- Python 3.12 managed by `uv`; each package has `pyproject.toml`, `src/<name>/`, `tests/`, and a `Makefile` with `test`, `lint`, `typecheck` targets that run pytest, ruff and mypy on that package only. The root `make check` runs all of them.
- `ruff` with rules E, F, I, B, UP, N, S, T20 (S101 ignored); `mypy --strict` on `engines` and `ledger`; coverage floors 90% on `engines` and `ledger`, 80% elsewhere.
- Dependency allowlist in `pyproject.toml` under `[tool.fund-intel.allowlist]`, one line per distribution with a reason: polars, pyarrow, pydantic, pydantic-settings, duckdb, numpy, httpx, dagster, dagster-aws, boto3, fastapi, uvicorn, redis, psycopg, sqlalchemy, alembic, anthropic, openai, mcp, vcrpy, lxml, openpyxl, python-dateutil, tenacity, opentelemetry-sdk, pytest, pytest-cov, hypothesis, ruff, mypy, import-linter. Adding anything else is a PR that changes the allowlist with a reason.
- Node 20 and pnpm 9 for `app`; `pnpm lint` and `pnpm typecheck` wired into `make check`.
- CI: GitHub Actions on every PR and on push to main; the golden job runs separately so a red golden case is visible on its own; secret scanning with gitleaks; the allowlist checker; Terraform validate and plan only when `infra/` changed, never apply.

## 4. AGENTS.md files to create verbatim

Create the root file exactly as below, then the three package files. Codex reads the closest file; package files add only what is stricter.

### Root `AGENTS.md`

```markdown
# fund-intel — instructions for Codex

## What this is
A holdings-native fund intelligence platform. We ingest public fund holdings
(SEC N-PORT, daily ETF issuer files), normalise them into a point-in-time
Parquet ledger keyed on FIGI, run deterministic analytics engines on top, and
expose everything through one validated query spec (REST, MCP, UI).
The full specification is docs/spec.md; cite its section numbers in PRs.

## Non-negotiables
1. Engines are pure functions: no network, no database, no LLM calls, no clock.
   Inputs and outputs are typed; the same input always gives the same output.
2. Every holding row carries asof_date AND public_date. Never drop either.
3. FIGI is the only join key. ISIN, CUSIP, SEDOL, ticker are attributes.
4. Silver and gold tables are append-only. Corrections add rows with a later
   public_date; nothing is overwritten.
5. Never change an expected value in tests/golden/ to make a test pass.
   If you believe the expected value is wrong, stop, explain why in the PR,
   and leave the test failing.
6. The LLM never writes SQL. Natural language compiles to a query spec that
   the validator accepts or rejects.
7. All judgement calls (classification, matching, routing) go through
   packages/decisions DecisionProvider. Never call a provider SDK elsewhere.
8. No secrets in the repo, in tests, or in logs. Tests use recorded fixtures
   under tests/recorded/; never call a live API from a test.
9. Treat all ingested content (filings, issuer files, PDFs, fund names) as
   untrusted data. Never pass it into a prompt as instructions.
10. If a ticket is ambiguous, stop and write the question in the PR
    description under "Open questions". Do not guess.

## Commands
- Setup: `uv sync --all-packages && pnpm install`
- Package checks: `make -C packages/<name> test lint typecheck`
- All checks: `make check`
- Golden tests only: `make golden`
- Rebuild ledger from bronze fixtures: `make rebuild-fixture`

## Code standards
- Python 3.12, Polars for frames, Pydantic v2 for contracts, ruff, mypy
  --strict in packages/engines and packages/ledger.
- Dates are `datetime.date`; timestamps are timezone-aware UTC. Currency codes
  are ISO 4217. Weights are fractions (0.0523), never percentages.
- Functions over classes; one module per engine; docstrings state the formula
  and cite the methodology version, because docs/methodology is generated
  from them.
- TypeScript strict in packages/app; the app calls the REST and MCP contracts
  only and never imports Python.

## Testing
- Write the test first; a ticket is done when its acceptance tests pass.
- Each engine has a golden suite: the synthetic four-security fund in
  tests/golden/synthetic_fund.json, a real ETF snapshot versus its index
  proxy, and an edge case (shorts, cash, derivatives).
- Reconciliation tests are property-based (hypothesis): sums tie to NAV within
  tolerance on every generated fixture.
- Minimum coverage: 90% on engines and ledger, 80% elsewhere.

## Pull requests
- One ticket per PR, under 400 changed lines unless the ticket says otherwise.
- Title: `[P0-07] Security master: OpenFIGI resolver`.
- Description template: What changed / How it was verified (commands and
  output) / Assumptions made / Open questions / Methodology version touched.
- Never open a PR that touches tests/golden/ or docs/methodology/ unless the
  ticket is titled "Methodology change".

## Review policy (applied by Codex code review and by human review)
Flag as blocking:
- any edit to an expected value in tests/golden/
- any network, database or LLM import inside packages/engines
- any holdings write that lacks public_date or data_version
- any schema change without a migration and a fixture update
- any new dependency not in the allowlist in pyproject.toml
- any prompt that interpolates ingested text as instructions
Flag as warning:
- functions over 60 lines in engines
- missing docstring formula on an engine function
- a test that mocks the function under test
```

### `packages/engines/AGENTS.md`

```markdown
# packages/engines — stricter rules (closest file wins)
- No I/O of any kind: no file reads, no network, no database, no environment
  variables, no clock. Engines receive Polars frames and typed settings as
  arguments and return a typed result object.
- Every public function returns a result object carrying methodology_version
  (semver string) and the hashes of the input frames it was computed from.
- One module per engine: classify.py, exposures.py, overlap.py,
  attribution.py, factors.py, alerts.py. Shared helpers live in _common.py.
- Docstrings state the formula in plain text; docs/methodology is generated
  from them, so a formula change without a docstring change is a defect.
- Golden tests are the specification. If an engine disagrees with a golden
  value, the engine is wrong until Nikhil says otherwise.
- Weights are fractions. Returns are fractions. Never percentages.
- mypy --strict and 90% coverage are enforced here.
```

### `packages/ledger/AGENTS.md`

```markdown
# packages/ledger — rules (closest file wins)
- Parquet layout: <root>/{bronze|silver|gold}/<table>/asof_month=YYYY-MM/
  vehicle_type=<etf|mutual_fund>/part-*.parquet. Fixtures mirror the same
  layout under tests/fixtures/ledger/.
- data_version is minted by ledger.versions.mint() on every successful silver
  write: a monotonic integer plus a UTC timestamp, recorded in
  _versions/manifest.json next to the data. Never reuse or hand-write one.
- Silver and gold are append-only. A correction is a new row with a later
  public_date. Deletion is not an operation.
- ledger.views is the ONLY reader of silver. Engines, access and ingest never
  read silver Parquet directly; they call views.latest_as_of and friends.
- Schemas are declared once in ledger.schemas as Pydantic models with matching
  pyarrow schemas; a schema change ships with a migration note and a fixture
  update in the same PR.
```

### `packages/app/AGENTS.md`

```markdown
# packages/app — rules (closest file wins)
- Next.js with TypeScript strict. The app talks to the REST and MCP contracts
  only; it never imports Python and never reads the ledger directly.
- Dashboards render saved query specs through fixed components. Never
  generate components, HTML or code from model output.
- Every number shown links to its provenance id from the API response.
- Design tokens live in app/tokens.css and are the only source of colour,
  type and spacing values.
- Accessibility floor: keyboard navigation, visible focus, contrast AA.
```

## 5. Data model

The system of record is Parquet on object storage in three layers (bronze raw documents, silver normalised rows, gold precomputed views); Postgres holds application state. Every silver and gold row carries `data_version`; every computed number carries `methodology_version`.

### Silver and gold tables

| Table | One row per | Columns | Partition |
| --- | --- | --- | --- |
| `holding` (silver) | fund, as-of date, security | `fund_id` str, `asof_date` date, `public_date` date, `figi` str or null, `provisional_id` str or null, `quantity` float or null, `market_value` float, `currency` str, `weight` float (fraction, as reported), `weight_reconciled` float, `asset_category` str, `freshness` str (`fresh` or `stale`), `source_doc_id` str, `source_ref` str, `data_version` int | `asof_month`, `vehicle_type` |
| `fund_nav` (silver) | fund, as-of date | `fund_id`, `asof_date`, `public_date`, `total_net_assets`, `flows_net` or null, `currency`, `data_version` | `asof_month` |
| `security` (silver) | security, validity window | `figi`, `isin`, `cusip`, `sedol`, `ticker`, `name`, `asset_class`, `issuer_lei`, `country`, `currency`, `valid_from`, `valid_to`, `data_version` | none |
| `price` (silver) | security, date | `figi`, `date`, `close`, `adj_close`, `currency`, `data_version` | `year` |
| `fx` (silver) | pair, date | `base`, `quote`, `date`, `rate` (quote units per one base unit), `data_version` | `year` |
| `fund` (silver) | fund (share class or ETF) | `fund_id`, `strategy_id`, `vehicle_type`, `domicile`, `issuer_id`, `benchmark_id`, `name`, `name_terms` list, `inception_date`, `data_version` | none |
| `strategy` (silver) | strategy | `strategy_id`, `issuer_id`, `canonical_name`, `match_method`, `match_score`, `data_version` | none |
| `factor_return` (silver) | factor, date | `factor_set`, `factor`, `date`, `return`, `data_version` | `year` |
| `exposure` (gold) | fund, as-of date, taxonomy node | `fund_id`, `asof_date`, `taxonomy_id`, `taxonomy_version`, `node_id`, `level`, `weight`, `data_version`, `methodology_version` | `asof_month`, `taxonomy_id` |
| `peer_set` (gold) | fund, as-of date, method, peer | `fund_id`, `asof_date`, `method`, `peer_fund_id`, `similarity`, `data_version`, `methodology_version` | `asof_month` |
| `holding_diff` (gold) | fund, date pair, security | `fund_id`, `from_date`, `to_date`, `figi`, `weight_from`, `weight_to`, `weight_change`, `event_type`, `data_version`, `methodology_version` | `to_month` |

### Postgres tables (application state, every row carries `tenant_id` with row-level security)

| Table | Purpose |
| --- | --- |
| `tenant`, `app_user`, `role`, `api_key` | Identity; roles admin, analyst, reviewer, api\_only |
| `taxonomy`, `taxonomy_version`, `taxonomy_rule` | User hierarchies; rules map securities to nodes by attribute, by explicit list, or by decision call |
| `classification` | security, taxonomy version, node, confidence, evidence text, evidence source id, reviewer, reviewed\_at |
| `policy` | Names Rule policy per fund: focus terms, thresholds, effective dates, version |
| `basket` | Saved fund sets and peer baskets |
| `saved_spec`, `dashboard` | Query specs and dashboard layouts as JSON |
| `alert_rule`, `alert_event` | Rule definitions and delivered events |
| `review_queue` | Unresolved names and failed reconciliations with priority = fund AUM times row weight |
| `workflow_run` | Mirror of workflow state for the UI |
| `audit_log` | Append-only: who ran which spec against which data version and methodology version |
| `source_document` | Document hash, URL, fetch time, parser version, page image references |

### Rules

- Bitemporal: `asof_date` is when the holding was true; `public_date` is when it became knowable. Research queries and the feed filter on `public_date` so a backtest never sees the future.
- Restatements never overwrite: a corrected row has a later `public_date`; the old row remains queryable.
- Identifiers: FIGI is the join key; ISIN, CUSIP, SEDOL and ticker are attributes. Unresolved names get a `provisional_id` of the form `prov:<sha1 of normalised name>` and a review-queue entry; they never join silently.
- Taxonomies are versioned; a query names a taxonomy version, so an edit never restates history.
- Weights are stored as reported (`weight`) and recomputed against reconciled net assets (`weight_reconciled`); engines use `weight_reconciled` unless a spec says otherwise.
- Cash and derivatives are explicit `asset_category` values and are reported as their own nodes, never folded into sectors or countries.

## 6. Ingestion pipelines

Every pipeline is a Dagster asset graph with the same shape: fetch to bronze, parse to a staging frame, reconcile, resolve identifiers, write silver with a new `data_version`, rebuild dependent gold assets. Nothing reaches silver unreconciled.

| Source | Cadence | Fetch | Parse | Reconciliation checks |
| --- | --- | --- | --- | --- |
| SEC EDGAR N-PORT | Poll daily; filings arrive quarterly about 60 days after quarter end | EDGAR index feeds filtered to form N-PORT-P; User-Agent with a contact email; at most 10 requests per second; skip by content hash | XML to `holding` and `fund_nav`; Part B supplies net assets and monthly flows; Part C holdings with identifiers that may be absent; derivatives tagged by `asset_category`, never dropped | Sum of market values within 1% of net assets after explained items (cash, derivatives, accruals); weights sum near 100% with cash and derivatives shown; identifier present or name queued |
| ETF issuer files | Daily after US and European close | Registry of issuers: `issuer_id`, `url_pattern`, `file_type` (csv or xlsx), `column_map`, `date_format`, `version`; hash dedupe; health SLO one file per trading day per issuer | CSV or XLSX to `holding`; a header not matching `column_map` is `SchemaDriftError`, never a guess | Weights sum within 1% of 100%; shares times price within tolerance of market value; row count within 20% of the prior day or flagged |
| OpenFIGI | On demand, daily batch | Free API, batched by identifier type, recorded fixtures in tests | Map ISIN, CUSIP, SEDOL, ticker to FIGI; collapse exchange-level FIGI to share-class FIGI for equities | Ambiguous matches go to the review queue |
| GLEIF | Weekly | LEI golden copy | Issuer entities and parents | Used for issuer rollups and bond issuer matching |
| Prices and FX | Daily | One vendor behind an interface (Polygon or Databento for US, EODHD for global and FX) | `price` with raw and adjusted closes; `fx` as quote units per one base unit | Missing-price rate per fund under 2% or the fund is flagged incomplete |
| Corporate actions | Daily | Vendor feed | Quantity adjustment across as-of dates | Split-adjusted position continuity test |
| Factor returns | Monthly | Ken French data library, AQR data sets | `factor_return` | Checksum against prior download |

### Entity resolution, in order

1. Exact identifier match to FIGI.
2. Learned name map: a table of `(normalised_name, issuer_hint) -> figi` that grows with every resolved row.
3. Bond parsing: issuer, coupon, maturity and currency parsed from the description, matched against the security master.
4. Decision call (`DecisionProvider`, choice among candidate FIGIs) returning a pick and a probability; a reasoning-model pass adds a quoted evidence string.
5. Below the confidence threshold: `provisional_id` plus a review-queue entry, prioritised by fund AUM times row weight.

### Data versioning and quality

- Each successful silver write mints an immutable `data_version` (monotonic integer plus UTC timestamp) in `_versions/manifest.json`; gold assets record which `data_version` they were built from.
- Freshness: every ETF row carries `freshness`; a missing issuer file marks that issuer's rows `stale`, and stale rows never enter gold.
- A daily quality report (Postgres row plus Markdown email) lists reconciliation failures, unresolved names, stale issuers and per-fund completeness; an incomplete fund is flagged, never dropped; the report is idempotent per `data_version`.
- `python -m ledger.rebuild --source <bronze> --target <ledger>` rebuilds silver and gold from bronze with per-stage timing; the same bronze and code must produce byte-identical silver part files.

## 7. Engines

Each engine is a pure Python function in `packages/engines` with a typed request and a typed result, no I/O, and a golden suite; the access layer fetches data through `ledger.views` and calls the engine, so the same code serves the UI, the API, agents and the feed.

| Engine | Inputs | Outputs | Formula (version 1.0.0) |
| --- | --- | --- | --- |
| `exposures` | holdings frame, taxonomy mapping (figi to node per level), settings | weight per node per level; cash and derivatives as their own nodes; unclassified weight | Sum of `weight_reconciled` per node; levels roll up exactly; totals equal 1.0 within 1e-9 |
| `overlap` | holdings frames for a basket, optional reference | pairwise overlap, active share versus reference, crowding per security across the basket | Overlap(F, G) = sum over securities of min(wF, wG); active share = 1 - overlap(F, B) = 0.5 sum of abs(wF - wB); crowding = count of funds holding and aggregate weight |
| `attribution` | fund and benchmark holdings at period start, security returns over the period, taxonomy mapping | allocation, selection, interaction per node; totals; fund, benchmark and active return; reconciliation in basis points | Brinson-Fachler, buy-and-hold weights, single period: allocation = (wF - wB)(rB\_node - rB); selection = wB (rF\_node - rB\_node); interaction = (wF - wB)(rF\_node - rB\_node); node returns are weight-averaged security returns; total effects must equal the active return within the configured tolerance |
| `factors` | fund return series, factor return set, window | betas, t-statistics, R-squared, residual volatility | Ordinary least squares of excess fund returns on factor returns over the window; no holdings used in version 1 |
| `classify` | holdings frame, taxonomy version with rules, decision provider results, policy (Names Rule mode) | node per security with confidence and evidence reference; unclassified list; Names Rule: 80% basket weight, deviation list with dates | Rule cascade: attribute rules, explicit lists, then decision-call choice with its probability as confidence, then an evidence pass on rows under the threshold; Names Rule mode evaluates each holding against the client's focus terms and sums qualifying `weight_reconciled` |
| `alerts` | holdings frames for two dates, rule set with threshold | events: new, exit, change, none, with weight change; drift versus label or peer median | new when weight goes from 0 to above 0; exit when from above 0 to 0; change when abs(weight change) is at least the threshold; otherwise none |

### Contracts

- Request objects are Pydantic models; frames are Polars DataFrames with the schemas in section 5. Results carry `methodology_version`, input frame hashes, and row-level provenance ids passed through from the holdings.
- `methodology_version` is semver per engine; a formula change increments it, the previous version stays callable for twelve months, and the docstring states the formula because `docs/methodology/` is generated from docstrings in CI.
- Performance budget: exposures, overlap and alerts under 200 ms for a 50-fund basket on gold and under 2 s on raw silver with a custom taxonomy; attribution under 3 s for one fund over one quarter; factor regression under 1 s per fund for a 60-month window.

### Golden suites per engine

- The synthetic fund in section 13 (exposures, overlap, crowding, attribution, alerts).
- A real ETF snapshot against its index-proxy ETF for two consecutive days, recorded as a fixture once with its actual period return.
- Edge cases: a short position, a cash-heavy fund, futures and swaps, a restated filing.

## 8. Decision calls

Every place the system chooses rather than writes goes through one interface in `packages/decisions`; the first backend is OpenAI's Decisions API, which returns typed predicates, choices and scores with probabilities and is priced per input token with no output charge. Deterministic engines still do all arithmetic.

### Interface

```python
class Question(BaseModel):
    id: str
    kind: Literal["predicate", "choice", "score"]
    text: str
    options: list[str] | None = None        # choice only
    range: tuple[float, float] | None = None # score only

class Answer(BaseModel):
    question_id: str
    value: bool | str | float
    probability: float                       # 0..1 for predicate and choice

class DecisionProvider(Protocol):
    def ask(self, input: str | bytes, questions: list[Question], *, question_set_version: str) -> list[Answer]: ...
```

- Backends: `openai_decisions` (default, behind a feature flag), `claude_structured` (structured output with a probability field), `rules` (deterministic lookups for tests and fallbacks).
- Every call is logged with backend, model, `question_set_version`, input hash and answers, so any classification can be replayed when the backend changes.
- Tests use the `rules` backend or recorded responses; a live call requires `FI_LIVE=1` and never runs in CI.

### Jobs

| Job | Question | Input | Use of the answer | Fallback |
| --- | --- | --- | --- | --- |
| Taxonomy classification | choice over leaf nodes | security record fields plus issuer description | node; probability is the confidence routing low scores to review | `claude_structured` |
| Names Rule test | predicate per holding against the client's focus definition | security record plus policy text | deviation list with probability; threshold per client | rules only |
| Entity resolution | choice among FIGI candidates | holding description plus candidate records | pick plus probability; below threshold to review | review queue |
| Query pre-route | predicate (fully specified?) plus choice (analysis type) | the user's question | below threshold returns a clarifying question; above it the orchestrator compiles the spec | orchestrator alone |
| Eval grading | predicate per rubric line | model output | pass or fail per rubric | model-graded rubric |
| PDF page triage (phase 4) | predicate (portfolio statement?) plus choice (which sub-fund) | page image | routes pages to the parser | layout heuristics |

### Rules

- Decision calls return answers, not reasons. Any row a client will see as evidence gets a second pass from a reasoning model that must quote a field from the security record or a stored document, with the source id; unquoted evidence fails validation.
- Probabilities are calibrated before they gate anything: 500 labelled securities per taxonomy family, Brier score and reliability curve written to `docs/methodology/`, thresholds set from the curve, re-checked on every model change.
- Full-universe classification cost planning: about 100,000 securities at about 300 input tokens each is about 30 million tokens per taxonomy run.
- Client taxonomy definitions and policy text are client intellectual property; the `claude_structured` backend stays ready for clients who restrict providers.

## 9. Access layer

One typed query spec is the contract for everything: the UI builds it, the API accepts it, the MCP server exposes it, and the LLM's only job is to compile natural language into it.

### Query spec (version 1)

```json
{
  "spec_version": "1",
  "universe": {"basket_id": "b_123"},
  "asof": {"date": "2026-09-30", "public_by": "2026-10-31"},
  "analysis": "exposures",
  "taxonomy": {"id": "tx_gics", "version": 4, "levels": 2},
  "compare_to": {"kind": "peer_median", "method": "holdings_knn"},
  "filters": [{"field": "vehicle_type", "in": ["etf"]}],
  "output": {"shape": "table", "limit": 500}
}
```

- `analysis` is one of `exposures`, `overlap`, `crowding`, `attribution`, `factors`, `alerts`, `classification`, `names_rule`, `holdings`.
- `universe` is a `basket_id`, an explicit `fund_ids` list, or a `strategy_id`; `compare_to` is `benchmark`, `peer_median`, `fund_id`, or absent.
- Validated against a published JSON Schema with Pydantic; unknown fields, out-of-range dates and missing taxonomy versions are rejected with a readable reason the orchestrator can repair.
- Every response carries `data_version`, `methodology_version`, the spec hash, and provenance ids per row.

### REST API (FastAPI)

- `POST /v1/query` spec in, result envelope out.
- `GET /v1/funds`, `GET /v1/securities`, `GET /v1/taxonomies/{id}`, `POST /v1/taxonomies`, `POST /v1/taxonomies/{id}/versions`, `GET /v1/alerts`, `GET /v1/baskets`, `POST /v1/baskets`.
- Feed: `GET /v1/feed/holdings` and `GET /v1/feed/holding-diffs`, paged, with `asof_from`, `asof_to`, `public_by` filters; bulk Parquet export with licence-tier metadata (`public`, `contributed`, `derived`).
- API keys per tenant and role; rate limits per plan; every call written to `audit_log`.

### MCP server

- Tools: `run_query(spec)`, `search_funds(text)`, `describe_taxonomy(id, version)`, `list_alerts(basket_id, since)`, `get_provenance(id)`; same validation, same audit log, same rate limits as REST.

### Orchestration (natural language to spec)

1. A decision-call pre-route answers two questions in one request: is the question fully specified (predicate) and which analysis type it needs (choice). Below the probability threshold the user gets a clarifying question.
2. Otherwise Claude is called with tools `search_funds`, `describe_taxonomy`, `emit_spec`; it resolves names to ids through the tools and emits a spec.
3. The validator accepts or returns a structured error; Claude repairs once. If the repair fails, the user gets a clarifying question. A guessed spec is never executed.
4. The engine runs; the narrative is written from the result table only, every sentence citing a row id; the UI renders the table and chart beside it.
5. Dashboards are JSON layouts of saved specs rendered by fixed components; the LLM edits layouts, never emits code.

### Evals

- A golden question set (200 by platform launch) with expected spec and expected numbers, run nightly in CI with Promptfoo; rubric checks (for example, every numeric claim cites a row id) run as decision-call predicates.
- Metrics: spec exact-match rate, number-match rate, refusal correctness on out-of-scope questions, latency. A drop below 90% number-match blocks the next release.
- Prompt caching for the stable system prompt and tool schema; a per-tenant cache of question-to-spec translations keyed on the question plus basket and taxonomy versions, 24-hour TTL.

## 10. Caching, performance and sizing

Four cache tiers keep interactive queries under two seconds while the system of record stays immutable Parquet; because engines are deterministic, every cache key is a hash of inputs and can never serve a stale number.

| Tier | What is cached | Key | Invalidation | Where |
| --- | --- | --- | --- | --- |
| 1. Gold pre-aggregations | exposures on standard taxonomies, peer sets, daily diffs, factor betas | fund, date, taxonomy version | rebuilt by Dagster on a new `data_version` | Parquet |
| 2. Query engine | hot partitions (last 24 months of silver, all of gold) and engine-native result cache | partition path | new `data_version` | DuckDB on local disk in version 1; ClickHouse later |
| 3. Application results | engine outputs | hash(spec, data\_version, methodology\_version, tenant taxonomy versions) | never; keys change when inputs change; LRU eviction | Redis |
| 4. Language layer | question-to-spec translations, prompt prefix | tenant, normalised question, basket version, taxonomy version | 24-hour TTL; provider prompt cache | Redis plus provider cache |

### Sizing and targets

- Rows per year: about 12,000 US mutual funds times 4 filings times 200 holdings is about 10 million; about 9,000 US and UCITS ETFs times 250 days times 300 holdings is about 670 million. Plan for 700 million rows a year, roughly 30 GB a year compressed.
- Most interactive queries touch 10 to 100 funds on a few dates after partition pruning, inside DuckDB's single-node range; the trigger for ClickHouse is more than about 20 concurrent interactive users or p95 above 2 s on custom-taxonomy queries, not volume.
- Latency targets: precomputed views p95 under 500 ms; custom taxonomy on raw silver for a 50-fund basket p95 under 2 s; natural-language round trip p95 under 8 s with the table rendered as soon as the engine returns.
- Engines run in a worker pool with per-request memory limits so DuckDB in-process cannot starve the API.

## 11. Workflows, security and tenancy

### Workflows

- Phase 2: scheduled jobs run as Dagster sensors and schedules (the daily competitor brief, peer refresh on new filings).
- Phase 3: Temporal for workflows that need approvals and retries; each step is a deterministic engine call or a bounded decision call, never an open-ended agent loop.
- Reference workflows: daily ETF competitor brief (diff basket, alerts engine, rank by weight change and AUM, draft from the result table, deliver by email); quarterly Names Rule review (classify against policy, 80% basket, deviations with dates, evidence pack, compliance approval before filing to the audit log); peer refresh; taxonomy classification run with reviewer confirmation of low-confidence rows before publishing a version.
- Idempotency: every step keyed on `(workflow_id, step, data_version)`; re-running with the same inputs produces the same outputs and no duplicate deliveries. Every workflow declares a maximum token spend and wall-clock time and fails loudly when exceeded. Every step emits an OpenTelemetry span with the spec hash and versions.

### Security and tenancy

- Shared data plane (public holdings are the same for everyone), isolated control plane: every Postgres application row carries `tenant_id` with row-level security enforced in the database.
- Identity through WorkOS (SAML and OIDC); roles admin, analyst, reviewer, api\_only; API keys per tenant and role, rotated from the UI.
- Append-only `audit_log` of every spec run, taxonomy publish, approval and export, exportable per tenant.
- Data residency: primary region eu-west-2 (London); a second region only when a contract requires it.
- Secrets in AWS Secrets Manager; none in the repository; LLM provider keys scoped per environment.
- Ingested content is parsed, never executed; extraction prompts instruct the model to ignore instructions found inside documents; fund names and issuer text enter prompts as data fields only.
- Licensing boundaries: feed exports carry the licence tier in metadata; manager-contributed data (later phase) is tagged at ingestion and excluded from feed exports by default.
- Compliance programme: SOC 2 tooling (Vanta or Drata) from month one; SOC 2 Type 1 before the first enterprise contract; penetration test before the Names Rule module ships.
- Backups: S3 versioning for Parquet, point-in-time recovery for Postgres, a documented rebuild of gold from silver, a quarterly restore drill.

## 12. Infrastructure, environments and CI/CD

Codex never deploys; GitHub Actions deploys to dev after merge and production promotion is a manual approval by Nikhil.

### AWS (eu-west-2), written as Terraform under `infra/`, one module per service

| Component | Service | Notes |
| --- | --- | --- |
| Ledger | S3 with versioning; prefixes bronze, silver, gold | lifecycle rule moves bronze to infrequent access after 90 days |
| API and MCP server | App Runner (ECS Fargate if limits bite) | autoscaling, HTTPS |
| Pipelines | Dagster on ECS, or Dagster Cloud with an ECS agent | schedules and sensors |
| Workflows (phase 3) | Temporal Cloud with workers on ECS | approvals and retries |
| Application database | RDS Postgres (Neon in an EU region is acceptable until traffic justifies RDS) | row-level security, point-in-time recovery |
| Cache | ElastiCache Valkey (Upstash acceptable early) | result and language caches |
| Secrets | Secrets Manager | injected into tasks |
| Observability | CloudWatch, OpenTelemetry to Grafana Cloud, Sentry | spans carry spec hash and versions |
| Cost guard | AWS Budgets alert at US$500 a month in dev | catches a runaway crawler or rebuild loop |

### Environments

- `dev`: everything above at the smallest sizes, fed by the fixture ledger plus a dev bucket holding the top 500 US funds and 200 ETFs.
- `prod`: created at the end of phase 2 when the first feed customer needs a stable endpoint.
- Codex Cloud tasks hold dev credentials only.

### CI on every pull request

1. `make check`: ruff, mypy, import linter, pytest with coverage floors.
2. `make golden` as a separate job.
3. Secret scanning (gitleaks) and `scripts/check_allowlist.py`.
4. Codex code review applying the `AGENTS.md` review policy.
5. Terraform validate and plan posted to the PR when `infra/` changed; never apply.

### On merge to main

1. Build images for `access` and `ingest`, push to ECR tagged with the commit SHA.
2. Terraform apply to dev; smoke test the API against the fixture ledger.
3. Production promotion as a manual approval step.

### Codex Cloud environment (Nikhil creates it; Codex writes the script)

- Repository `fund-intel` connected; setup script `codex/environment-setup.sh` installs uv and pnpm, runs `uv sync --all-packages` and `pnpm install`, installs the DuckDB CLI, and runs `make rebuild-fixture` so a small ledger exists before any task starts.
- Secrets declared in the environment configuration: dev-scoped AWS keys for one dev bucket, `OPENFIGI_API_KEY`, `MARKET_DATA_API_KEY`, `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` used only behind `FI_LIVE=1`. Nothing production-scoped.
- Network allowlist: package registries, GitHub, sec.gov, the five issuer domains in the registry, api.openfigi.com, the market-data vendor. Tests never need the allowlist.

### GitHub

- Branch protection on main: CI green, Codex code review completed, one human approval, CODEOWNERS satisfied for `tests/golden/`, `docs/methodology/`, all `AGENTS.md` files and `pyproject.toml`.
- Dependabot or Renovate weekly with lockfiles committed.

## 13. Golden fixture: synthetic fund

Create `tests/golden/synthetic_fund.json` from these tables exactly; the engines in phase 1 are tested against it, and no value here may be changed by Codex. All weights and returns are fractions. Tolerances: weights and returns 1e-9 absolute; attribution reconciliation 5 basis points; alert threshold 0.03 absolute weight change.

### Inputs

| Security | FIGI | Sector | Country | Fund1 day 1 | Bench | Fund2 | Fund3 | Fund1 day 2 | Period return |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | BBG00SYNTH00A | Tech | US | 0.40 | 0.20 | 0.10 | 0.30 | 0.45 | 0.12 |
| B | BBG00SYNTH00B | Tech | US | 0.20 | 0.30 | 0.50 | 0.20 | 0.15 | 0.04 |
| C | BBG00SYNTH00C | Health | UK | 0.25 | 0.25 | 0.20 | 0.20 | 0.25 | -0.03 |
| D | BBG00SYNTH00D | Health | US | 0.15 | 0.25 | 0.20 | 0.20 | 0.00 | 0.06 |
| E | BBG00SYNTH00E | Health | US | 0.00 | 0.00 | 0.00 | 0.00 | 0.15 | 0.01 |
| Cash | CASH | Cash | - | 0.00 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 |

### Expected exposures by sector

| Node | Fund1 day 1 | Bench | Fund2 | Fund3 |
| --- | --- | --- | --- | --- |
| Tech | 0.60 | 0.50 | 0.60 | 0.50 |
| Health | 0.40 | 0.50 | 0.40 | 0.40 |
| Cash | 0.00 | 0.00 | 0.00 | 0.10 |

### Expected exposures by country (cash reported separately, not as a country)

| Node | Fund1 day 1 | Bench | Fund2 | Fund3 |
| --- | --- | --- | --- | --- |
| US | 0.75 | 0.75 | 0.80 | 0.70 |
| UK | 0.25 | 0.25 | 0.20 | 0.20 |
| Cash | 0.00 | 0.00 | 0.00 | 0.10 |

### Expected overlap and crowding

- Overlap Fund1 versus Bench: 0.80. Active share Fund1 versus Bench: 0.20 (both as 1 minus overlap and as 0.5 times the sum of absolute weight differences).
- Overlap Fund1 versus Fund2: 0.65.
- Crowding across Fund1, Fund2 and Fund3 (count of funds holding, aggregate weight): A 3, 0.80; B 3, 0.90; C 3, 0.65; D 3, 0.55; E 0, 0.00; Cash 1, 0.10.

### Expected attribution (Brinson-Fachler by sector, Fund1 day 1 versus Bench)

- Fund return 0.0575; benchmark return 0.0435; active return 0.0140.
- Tech: wF 0.60, wB 0.50, fund sector return 0.0933333333, benchmark sector return 0.0720; allocation 0.00285, selection 0.0106666667, interaction 0.0021333333, total 0.01565.
- Health: wF 0.40, wB 0.50, fund sector return 0.00375, benchmark sector return 0.0150; allocation 0.00285, selection -0.005625, interaction 0.001125, total -0.00165.
- Totals: allocation 0.0057, selection 0.0050416667, interaction 0.0032583333, total 0.0140. Reconciliation to active return: 0.0 basis points.

### Expected alerts (Fund1 day 1 to day 2, threshold 0.03)

| Security | Day 1 | Day 2 | Change | Event |
| --- | --- | --- | --- | --- |
| A | 0.40 | 0.45 | 0.05 | change |
| B | 0.20 | 0.15 | -0.05 | change |
| C | 0.25 | 0.25 | 0.00 | none |
| D | 0.15 | 0.00 | -0.15 | exit |
| E | 0.00 | 0.15 | 0.15 | new |
| Cash | 0.00 | 0.00 | 0.00 | none |

### JSON shape

```json
{
  "name": "synthetic_fund",
  "methodology_version": {"exposures": "1.0.0", "overlap": "1.0.0", "attribution": "1.0.0", "alerts": "1.0.0"},
  "tolerances": {"weights_abs": 1e-9, "returns_abs": 1e-9, "attribution_reconciliation_bp": 5, "alert_threshold_abs": 0.03},
  "inputs": {"securities": [ {"security": "A", "figi": "BBG00SYNTH00A", "sector": "Tech", "country": "US", "fund1_day1": 0.40, "bench": 0.20, "fund2": 0.10, "fund3": 0.30, "fund1_day2": 0.45, "period_return": 0.12 } ] },
  "expected": {"exposures": {}, "overlap": {}, "crowding": {}, "attribution": {}, "alerts": []}
}
```

Fill `inputs.securities` with all six rows and `expected` with every table above, using the same field names shown in the tables (lower-case with underscores).

## 14. Phase 0 tickets

One pull request each, in this order; P0-01 to P0-03 are sequential, P0-04 to P0-12 may run as parallel tasks once P0-03 has merged. Each acceptance line is a test written before the implementation.

### P0-01 Scaffold the monorepo

- Goal: every package exists with the same three Make targets, CI is green, the import linter enforces section 3, the `AGENTS.md` files from section 4 are in place, the spec is saved as `docs/spec.md`. No business logic.
- Create: all files in section 3; each package with `pyproject.toml`, `src/<name>/__init__.py` exporting `__version__ = "0.0.1"`, `tests/test_smoke.py`, `Makefile`; `packages/app` as a Next.js TypeScript-strict placeholder with `lint` and `typecheck` scripts; `tests/golden/test_golden_smoke.py` that loads `synthetic_fund.json` and asserts `methodology_version` is present; `tests/fixtures/bronze/.gitkeep` and `tests/fixtures/ledger/.gitkeep`.
- Acceptance: `make check` exits 0 from a clean checkout; a deliberate `from access import *` in `engines` makes `lint-imports` fail (prove, then revert); adding `requests` to any package makes `check_allowlist.py` fail (prove, then revert); `make golden` passes; the CI workflow runs on the PR with all jobs green and terraform-plan skipped.

### P0-02 Ledger schemas, Parquet layout, data\_version minting

- Create in `packages/ledger/src/ledger/`: `schemas.py` (Pydantic models and pyarrow schemas for every silver table in section 5), `layout.py` with `partition_path(layer, table, asof_date, vehicle_type) -> str`, `io.py` with `write_silver(table, frame, root) -> int` (append-only; a new part file per write) and `read_silver(table, root, asof_month=None)`, `versions.py` with `mint(root) -> DataVersion` and `current(root)`.
- Acceptance: round trip of every schema preserves fields and dtypes; `partition_path("silver", "holding", date(2026, 9, 30), "etf") == "silver/holding/asof_month=2026-09/vehicle_type=etf/"`; two successive writes mint strictly increasing versions and both part files stay readable; a frame missing `public_date` raises `LedgerValidationError` and leaves the directory unchanged (property test over random column drops); writing one million synthetic holding rows completes in under 30 s on the CI runner.

### P0-03 Holdings view library

- Create `packages/ledger/src/ledger/views.py`: `latest_as_of(root, fund_ids, asof_date, public_by=None)` returning one row per (fund\_id, figi or provisional\_id) choosing the row with the greatest `public_date` not exceeding `public_by`; `holdings_history(root, fund_id, start, end, public_by=None)`; `two_dates(root, fund_id, d1, d2, public_by=None)` returning two frames with identical columns.
- Acceptance: rows (public 2026-08-29, weight 0.10) and (public 2026-09-15, weight 0.12) for one holding give 0.10 with `public_by=2026-09-01` and 0.12 without; property test that the chosen row always has the maximum admissible `public_date` and no key appears twice; reads never mutate files; a 100-fund, 24-month fixture answers 50 funds in under 500 ms.

### P0-04 EDGAR N-PORT fetcher

- Create `ingest/nport/fetch.py`: `list_new_filings(since, client) -> list[FilingRef]`, `fetch_to_bronze(ref, bronze_root, client) -> BronzeRecord`; Dagster asset `nport_bronze` scheduled daily; EDGAR fair-access headers and rate limit; dedupe by accession number and content hash.
- Acceptance: a recorded index fixture yields the expected FilingRef list; fetching the same filing twice writes one bronze object; the asset materialises in Dagster's test harness.

### P0-05 N-PORT parser

- Create `parse_filing(xml_bytes) -> ParsedFiling` with `.holdings`, `.nav`, `.warnings`; derivatives tagged with `asset_category`; missing identifiers tolerated.
- Acceptance: three recorded filings parse to the row counts and net assets recorded in `tests/recorded/nport/expected.json`; a malformed filing raises `NportParseError`; derivatives appear with `asset_category` set.

### P0-06 Reconciliation

- Create `reconcile(parsed, tolerance=0.01) -> ReconcileResult` with `.ok`, `.failures`, `.explained`; recomputes `weight_reconciled`; routes failures to `review_queue`.
- Acceptance: property test with generated holdings always passes within tolerance; an injected 3% error is caught and routed; failure objects carry filing id, check name and delta.

### P0-07 Security master and resolver

- Create `resolve(frame, client, name_map) -> ResolvedFrame`, the `NameMap` Parquet table, `parse_bond_description(text) -> BondParts | None`, an OpenFIGI client on recorded fixtures, and a stub `DecisionProvider` call using the `rules` backend (real backend in P1-02).
- Acceptance: 95% of identifiers in the three recorded filings resolve; a fifty-name messy fixture (create it, including two deliberate ambiguities) resolves at least 40 and routes both ambiguities to review; the name map grows after a run and the second run resolves faster.

### P0-08 ETF issuer crawler registry and five crawlers

- Create the registry schema from section 6, `crawl(issuer_id, trade_date, client) -> BronzeRecord`, `parse_issuer_file(issuer_id, bytes) -> DataFrame`; crawlers for the five largest US ETF issuers by assets; record one fixture file per issuer with secrets and personal data absent.
- Acceptance: each fixture parses to a frame whose weights sum within 1% of 100%; a renamed column raises `SchemaDriftError`; hash dedupe skips an unchanged file.

### P0-09 Crawler health and freshness

- Create `health_report(registry, bronze_root, today) -> HealthReport`, the `freshness` column on every ETF silver row, and stale-row exclusion in gold rebuilds. SLO: one successful file per trading day per issuer by 09:00 local market time the next day.
- Acceptance: a missing day marks that issuer's rows stale; a stale row never appears in a gold rebuild fixture; the report serialises to JSON.

### P0-10 Prices, FX and corporate actions

- Create the vendor client on recorded fixtures, `price` and `fx` silver writes, and `adjust_for_actions(holdings, actions)`.
- Acceptance: missing-price rate per fund computed and a fund above 2% flagged incomplete; a fixture 2-for-1 split keeps position value continuous.

### P0-11 Daily quality report

- Create the Dagster asset `quality_report` producing a Postgres row and a Markdown email with the four sections in section 6.
- Acceptance: a fixture ledger produces expected counts per section; re-running on the same `data_version` inserts no second row.

### P0-12 Rebuild from bronze

- Create `python -m ledger.rebuild --source <bronze> --target <ledger>` running parse, reconcile, resolve and write for every bronze object with per-stage timing; non-zero exit on any reconciliation failure.
- Acceptance: fixture rebuild completes and matches the previous silver byte for byte; timing printed per stage.

### Phase 0 exit gate (checked by Nikhil on the dev bucket)

95% of holdings rows resolved to FIGI on the top 500 US funds and 200 ETFs, 98% of filings reconciled, full rebuild from bronze in under one hour, crawler health green for five consecutive days.

## 15. Phases 1 to 3 tickets

Same ticket shape, same rules. Engine tickets are tested against section 13 and the real-ETF fixture; nothing ships with a red golden test.

### Phase 1: engines and decision calls

- P1-01 `DecisionProvider` interface from section 8, the `rules` backend, a recorded-response harness, and call logging.
- P1-02 `openai_decisions` backend behind a feature flag; `claude_structured` backend; both selectable by configuration.
- P1-03 Calibration harness: 500 labelled securities (Nikhil supplies the labels as a CSV in a Methodology change PR), Brier score and reliability curve written to `docs/methodology/calibration.md`.
- P1-04 `exposures` engine with multi-level taxonomies. Golden: section 13 sector and country tables; levels roll up exactly; cash as its own node.
- P1-05 `overlap` engine. Golden: overlap 0.80 and 0.65, active share 0.20 both ways, crowding counts and aggregate weights from section 13.
- P1-06 `attribution` engine. Golden: every value in the section 13 attribution block; reconciliation 0.0 bp on the synthetic fund and within 5 bp on the real-ETF fixture.
- P1-07 `alerts` engine. Golden: the six events in section 13 at threshold 0.03; drift versus label computed from exposures.
- P1-08 `classify` engine: rule cascade, decision-call stage, evidence-pass contract, Names Rule mode with the policy model from section 5. Golden: a ten-security taxonomy fixture with explicit expected nodes (create it with obvious cases) and a Names Rule case where exactly one holding fails the focus definition.
- P1-09 `factors` engine: OLS on public factor sets. Golden: a synthetic return series built from known betas recovers them within 1e-6.
- P1-10 Gold rebuild assets in Dagster for `exposure`, `peer_set` (holdings nearest neighbours by overlap) and `holding_diff`, keyed on `data_version`.
- P1-11 Methodology document generator from engine docstrings, run in CI, output under `docs/methodology/`.

### Phase 2: access layer and feed

- P2-01 Query spec JSON Schema and Pydantic validator; a malformed-spec test set of 100 cases, all rejected with readable errors.
- P2-02 FastAPI service with every endpoint in section 9; result envelope with versions and provenance ids.
- P2-03 Result cache keyed on spec, data, methodology and taxonomy versions.
- P2-04 Feed endpoints and bulk Parquet export with licence-tier metadata.
- P2-05 Postgres schema from section 5 with migrations (Alembic), row-level security, API keys, audit log.
- P2-06 MCP server exposing the tools in section 9.
- P2-07 Daily competitor brief as a Dagster sensor delivering by email from the alerts engine output.

### Phase 3a: platform

- P3-01 Next.js app shell with WorkOS SSO, tenant switching, design tokens.
- P3-02 Baskets and taxonomy editor (versioned publish, rule types from section 5).
- P3-03 Exposure and overlap views rendering saved specs; provenance links on every number.
- P3-04 Daily ETF alerts view and alert rules.
- P3-05 Orchestration from section 9 with the pre-route, the clarify-never-guess fallback, and the nightly 200-question eval.
- P3-06 Dashboards as saved-spec layouts.

### Phase 3b: Names Rule and compliance

- P3-07 Policy editor: focus terms, thresholds, effective dates, versions per fund.
- P3-08 Names Rule mode end to end: classification with evidence pass, 80% basket, deviation list with dates, quarterly evidence pack as PDF.
- P3-09 Temporal workflow for the quarterly review with a compliance approval step.
- P3-10 SOC 2 tooling integration, security questionnaire answers generated from repository controls, penetration-test fixes.

## 16. Definition of done and gates

### A ticket is done when

- Its acceptance tests exist, were shown failing first, and pass.
- `make check` and `make golden` are green; coverage floors hold.
- The PR template is complete and "Open questions" is empty.
- Codex code review has run and no blocking finding remains.
- Nikhil has merged it. Nothing else counts as done.

### Phase gates

| Phase | Gate |
| --- | --- |
| 0 | 95% of rows resolved to FIGI on the top 500 US funds and 200 ETFs; 98% of filings reconciled; rebuild from bronze under one hour; crawler health green five days running |
| 1 | Every golden test green; exposures on a 50-fund basket under 2 s on raw silver; decision probabilities calibrated on 500 labelled securities with the Brier score recorded |
| 2 | Feed export validated end to end including `holding_diff`; 100% of the malformed-spec set rejected; the daily brief delivered from a Dagster sensor |
| 3a | 200 golden questions at 90% number-match; latency targets met; MVP signed off by Nikhil |
| 3b | Names Rule evidence pack reviewed by Nikhil against a known deviation; approval workflow pauses and resumes; SOC 2 Type 1 audit scheduled |

### What Codex must never do

- Edit an expected value under `tests/golden/`.
- Import a network client, database driver or LLM SDK inside `packages/engines`.
- Write a holdings row without `public_date` and `data_version`.
- Let the LLM emit SQL, or execute a spec that failed validation.
- Call a provider SDK outside `packages/decisions`.
- Put ingested text into a prompt as instructions.
- Add a dependency outside the allowlist without changing the allowlist in the same PR with a reason.
- Deploy, apply Terraform, or touch anything production-scoped.
- Guess when a ticket is ambiguous; ask under "Open questions" instead.
