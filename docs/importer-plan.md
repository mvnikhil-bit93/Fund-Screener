# Holdings importer plan

Updated 7 November 2026 after approval of identified money-market fund-unit support
and daily historical holdings for at least three years, or since inception.
This is a proposed implementation plan, not an implemented importer or source-use
approval.
Issuer discovery sites are now reachable. The [live assessment](issuer-assessment.md)
records terms applicability, access gates, Avantis's official All Holdings/export
route, and JPMorgan's actual JGRO Excel downloads. Files for 5 and 6 November
are now captured; a complete first-source contract and accepted fund roster remain open.

**Historical source feasibility is the next prerequisite.** The
[historical-source assessment](historical-sources.md) compares issuer archives and
commercial candidates. No inspected source yet establishes the required daily
backfill. Select the acquisition source before committing to an issuer-specific
HTML/XLSX adapter; the eventual contract may use historical and ongoing delivery
from different providers if their compatibility is demonstrated.

The subsequent [JPMorgan validation](jpmorgan-source-validation.md) screens all
31 active equity funds and records a repeat acquisition with unchanged financial
data. Identified money-market fund units are now supported as distinct securities;
actual instrument and source admission remain unresolved. The scope approval does
not establish a complete first-source contract for M04.

The expandable research inventory is [issuer_sources.json](../config/issuer_sources.json),
with a [CSV view](issuer-sources.csv) and [register guide](source-register.md).
The financial and dependency contracts remain [specification v1.1](spec.md).

## 1. Complete the first-source evidence gate — M00

Capital Group and Avantis were the initial discovery priorities. Current evidence
supports comparing Avantis's All Holdings HTML/client CSV route with JPMorgan's
direct XLSX route. Capital Group still needs a public or authorized daily route.
Avantis's notice describes each position's disclosure before trading each business
day, and its AVUS export mechanism is verified. JGRO has a real standalone file;
its two weight bases and negative cash need explicit treatment. Both candidates
need field-use decisions and an eligible fund contract. The other reviewed issuers
need route-specific investigation of terms and any observed access gates. General
website restrictions do not by themselves prove that factual holdings require a
paid licence. Select US-listed, USD-reporting, active, long-only equity ETFs with
complete disclosed portfolios. Exclude unsupported derivatives, short/inverse/leverage strategies,
and funds whose published baskets or proxy portfolios are not their actual full
holdings. An issuer's product label alone does not establish fund eligibility.

Aim for one issuer with at least ten eligible funds for the pilot. Record a
coverage shortfall and resolve the roster before adding another issuer; do not
fill the universe with unsuitable funds to meet the count.

For each candidate source, complete the following evidence before selecting it:

| Evidence | Decision it supports |
| --- | --- |
| Official fund page, issuer fund ID, ticker, full-holdings link, and actual redirect chain | Establish the authoritative endpoint and fund identity |
| Applicable website, disclosure/file and tool terms; scope, evidence versions, reviewed basis and reviewer | Assess access method, original-document retention, factual-data analysis/display, derived analytics, third-party additions and redistribution separately |
| Two permitted files from distinct portfolio dates, with retrieval metadata and hashes | Test real format variation and avoid mistaking two downloads of one date for historical coverage |
| Per-fund date inventory across three years or since inception, plus actual historical samples spanning the period and consecutive dates | Establish historical feasibility before adapter selection; two recent files alone are insufficient |
| Historical provenance, revisions, identifier continuity, delivery/use basis and backfill/recurring costs | Evaluate the proposed archive and ongoing source together, including any source transition |
| Portfolio date field, timezone, evidenced publication metadata, calendar, and deadline | Distinguish source valuation date, retrieval time, and lateness |
| File type, sheets/sections, column names, units, identifiers, row count, and full-portfolio evidence | Define the parser and completeness checks |
| Reported denominator, decimal precision, total weight, residual, and unsupported rows | Establish which calculations the source can support without normalization |

Assess the specific access method and use of specific material. Facts generally
are not protected as such by US copyright, while website expression, compilation,
contractual access conditions, and proprietary additions raise separate questions.
A reviewed use basis may be an applicable licence or a documented legal basis
for factual use; lack of an express grant alone proves neither a prohibition nor
a need to buy data. Public access and robots directives also do not settle reuse.
Record unresolved material rights as unresolved: permitted investigation may
continue, while customer-facing use remains disabled under the specification.
Retaining an original document or publishing a fixture is a separate operation
from using its factual observations. Do not infer rights from another issuer's
terms, or assume all derived analytics are unrestricted.

Discover download hosts from issuer links and actual responses. Review exact
new hosts through environment settings; do not guess CDN patterns, add wildcard
access, route around blocked hosts, or bypass consent/authentication challenges.
If only today's file is available, prospective capture can add format evidence,
but cannot establish the required backfill. Investigate an evidenced archive or
alternative provider; do not invent an archive or relabel synthetic files as
issuer evidence. Complete acquisition/reconciliation of the approved historical
inventory follows implementation and is required before pilot sign-off.

The source decision records technical suitability and the reviewed basis for
each use separately. Unknown evidence cannot become an approval through a
default value.
Choose the first adapter only after these findings support a concrete source
contract; unresolved commercial rights remain an explicit pilot blocker.

### Verified current delivery choices to compare after historical sourcing

| Candidate | Acquisition evidence | Implication for the first adapter |
| --- | --- | --- |
| Avantis AVUS | Official All Holdings HTML contains the same 1,943 rows as its product page. The issuer's client-side export builds a CSV from those rows; no browser-generated CSV was captured. | A bounded HTML-data extractor is a concrete option. Document the artifact honestly; do not invent a server CSV URL. Export does not increase weight precision and replaces empty/falsy values with a marker. |
| JPMorgan JGRO | Official Download All Holdings control returned a 140-position XLSX; fund/date are inside the workbook and match issuer dailyHoldingsAll metadata. | A direct-file acquisition/parser candidate. Version the Holdings sheet layout, preserve both weight columns, signed values/quantities and missing IDs. |

The Avantis Daily Pricing Basket is a separate dataset and must not replace the
actual portfolio. JGRO's % of Market Value and % of Net Assets are distinct bases;
do not prefer the former merely because its displayed total is 100%. Net-assets
weights total 100.06% on 5 November, and negative cash rounds to zero in both
columns. The 6 November file totals 100.05% of net assets and has no negative
quantities/values. No basis is approved as analytical W by this comparison.
The two-date format evidence is established for JGRO; fund/date acceptance and
a suitable roster remain necessary whichever delivery format is selected.

The full JPMorgan screen finds money-market investments in every active equity
fund. Five candidates avoid observed derivative/short, negative-cash and non-USD
cash issues, but still need instrument identities and the other
M00 gates. Do not present them as an approved roster or silently reduce the target
of ten funds. The proposed net-assets denominator remains unadopted while the
source-reference reconciliation and comparison basis are unresolved.

The approved money-market category preserves each actual share class, reported
weight, quantity and value. It does not convert those holdings to cash or infer
identity from an abbreviated source label. Parser mapping must retain unresolved
rows until the instrument evidence supports the category and identity; M06 owns
the reviewed mappings. The approved extension leaves other asset and metric gates
unchanged.

### Proposed field profile for the first source

Start with the facts needed to compare disclosed portfolios. Record the selected
fields and their use basis explicitly in the source contract:

| Material | Proposed treatment |
| --- | --- |
| Fund identity, portfolio date, reported security name/ticker, quantity, value, weight and units | Candidate factual observations; preserve reported precision, provenance and unresolved semantics; assess the actual route and intended use |
| CUSIP, ISIN, SEDOL and cross-source mappings | Review namespaces, applicable provider conditions and identity evidence separately; presence in a public file is not blanket mapping approval |
| Source security type, sector and country labels | Preserve necessary source evidence where permitted; do not automatically adopt a proprietary taxonomy or equate country with issuer domicile |
| Commentary, ratings, marketing graphics and third-party research | Exclude from the analytical field profile unless separately needed and reviewed |
| Original HTML, CSV, workbook or other artifact | Keep exact bytes in restricted immutable evidence storage only under the reviewed retention basis; customer document delivery and public Git publication require separate decisions |

This profile limits copied additions, not the portfolio's positions. Every
position remains represented in candidate assessment, including unsupported
instruments; selecting fields must not hide exposure or remove rounded-zero
rows. The internally defined, manually reviewed taxonomy and identity workflow
remain M06. Private storage controls do not themselves establish retention rights.

## 2. Build one bounded acquisition path — M04, after M00 and M02

Implement one source adapter against the verified file format and URLs. Keep
HTTP retrieval and source-specific rules in ingest; keep immutable-object I/O
and readers in ledger. Reuse ledger.types.SourceDocument and existing canonical
contracts. Add a versioned retrieval/observation record for evidence not currently
represented there, rather than hiding it in filenames or logs.

The future runtime configuration must accept only verified records approved for
the requested operation. A research-capture approval does not enable production
display. Validate source ID, fund ID, explicit HTTPS endpoints, allowed hosts,
contract version, rights scope, and operational limits before any request.
Research seed URLs and unreviewed register rows are never executable defaults.

Distinguish an issuer's research/discovery configuration from an enabled runtime
contract. Carry exact scoped rights-decision IDs, evidence versions, reviewed
basis, material/field scope, expiry or review dates, and conditions into runtime
validation. Treat explicit access restrictions separately from a factual-use
basis: the latter does not authorize an otherwise restricted retrieval method.
A reachable page or limited download licence is not approval for all recurring
retrieval, retention, and display operations.

1. Fetch one selected fund/date, recording the requested URL and each redirect.
   Check every destination before following it; retain normal TLS verification,
   configured proxy routing, and source-specific access requirements.
2. Stream into a bounded temporary object, validate the response, and calculate
   SHA-256 over the exact downloaded artifact. Reject HTML error/consent pages
   masquerading as CSV/XLSX, incomplete responses, and oversized payloads. If an
   approved contract explicitly uses issuer HTML with embedded structured data,
   preserve that HTML and use a versioned, non-executing extractor; never treat
   arbitrary page HTML as an accepted holdings response.
3. Commit the complete original artifact through ledger's immutable storage
   boundary. Keep downloaded artifact bytes distinct from any decoded or parsed
   representation; record transport encoding and the hashing convention.
4. Persist credential-safe URL/redirect evidence, fetched_at UTC, hash, byte length, content type,
   adapter version, and a restricted response-metadata allowlist. Never retain
   authorization headers, cookies, or signed URL credentials in logs, the source
   register, CSV exports, or Git. Redact credential-bearing query parameters and
   mark the redaction; a redacted provenance URL is not an executable endpoint.
5. Deduplicate stored objects by content hash while retaining each observation.
   Preserve the earliest successful observation of an exact source revision;
   later retrievals must not reset that knowledge time. Identical bytes do not
   establish a new portfolio date. Changed bytes for the same fund/date remain
   candidates for amendment assessment, not automatic accepted replacements.

HTML presentation or unrelated page content can change while holdings stay the
same. Preserve each original hash and observation, then compare the extracted
canonical candidate independently; raw-page changes alone do not establish a
financial correction. A fund fact sheet, creation basket, or proxy portfolio
cannot substitute for the complete holdings artifact specified by the contract.
Use the verified canonical US routes in runtime configuration: the Avantis
legacy catalog route looped between slash variants, while its canonical US
catalog succeeded. This is evidence for canonicalization and redirect-loop tests,
not a reason to raise redirect limits or guess archive endpoints. Quarterly
document hosts need separate network/terms verification and are not daily feeds.

Proposed initial limits below require confirmation against issuer terms and
measured samples. A source's stricter requirements take precedence.

| Control | Proposed initial bound |
| --- | --- |
| Request concurrency and spacing | One request per issuer at a time; at least 2 seconds between requests |
| Timeouts | 10-second connection, 30-second idle read, 60-second total request |
| Redirects and attempts | At most 3 redirects; 3 attempts total for transient failures |
| Retry behavior | Respect Retry-After and use bounded backoff; defer rather than exceed the run deadline |
| Download/decompression | 25 MiB downloaded artifact, 100 MiB decoded/unpacked content, 100:1 expansion ceiling |
| Workbook/parsing resources | 20 sheets, 100,000 rows, 200 columns; never execute macros or formulas |
| Explicit development run | 10-minute total deadline; no automatic recurring schedule |

Treat authentication/permission failures as configuration outcomes, not an
invitation to retry indefinitely. Apply decompression limits while streaming or
reading archive members; do not decompress an unbounded file before checking it.

## 3. Parse and assess candidates — M05, after M04

Map verified source columns to Snapshot, Position, and candidate Instrument
records. Preserve the original text/decimal precision, identifiers, file/sheet/
row provenance, source sections, parser version, and quality reasons. Convert
percentages to decimal fractions only when the source unit is established.
Keep missing values missing; do not guess identity from a name or replace an
absent weight with zero. Source-scoped provisional identities need evidence and
discriminating fields; shared identity resolution remains M06.

The observed Avantis layout includes percentage strings with two decimal places.
Preserve that source precision and distinguish a displayed 0.00% from a missing
weight or proof of an economically zero position. Record a raw all-row weight
sum separately from admitted analytical W; do not apply the analytical residual
gate to an unverified denominator or silently discard unsupported rows. Version
field mappings against the exact artifact schema and supporting sample hashes.
For JPMorgan, the observed workbook has header row 8 and an internal portfolio
date in H6. Preserve % of Market Value and % of Net Assets separately; their
header labels establish distinct reported bases, while operational semantics and
cross-fund comparability still need the source contract. Retain negative quantities
and market values even when displayed weights round to zero. A money-market
position is not automatically explicit cash. Ticker-only rows need identity
resolution; a populated securityId in parallel product JSON is only a lead until
its namespace and join are verified. Do not infer CUSIP from its character shape.
AVUS and AVUV contain sweep vehicles and rights; AVUS also contains warrants and
preferred stock. Do not silently treat pooled sweep vehicles as explicit USD
cash or remove rounded-zero unsupported positions. The source-admission decision
must resolve those cases within the current scope or obtain a separately reviewed
scope/methodology change. Current evidence does not admit either fund.

Read asof_date from evidenced portfolio metadata. Keep it separate from
first_observed_at and fetched_at; populate source_published_at only with evidence.
Treat each disclosure as a whole candidate snapshot. A security omitted from a
new complete snapshot is absent, not carried forward from an older disclosure.

Compute W and residual = 1 - W using the reported analytical basis. Preserve
negative residuals and never invent cash or rescale weights to balance a file.
Under the current contract, unexplained absolute residual above 0.01 quarantines
the candidate; absolute residual above 1e-9 through 0.01 prevents unit-total metrics.
Full overlap/active share additionally require complete, compatible portfolios,
resolved identities, and nonnegative weights. Unsupported assets/currency,
negative weights, missing sections, or ambiguous denominators block eligibility.
Record source completeness, identity coverage, classification coverage, and
numerical completeness separately. Missing classifications stay Unclassified.

## 4. Acceptance and delivery sequence

Write failing behavior tests before the corresponding M04/M05 implementation.
Keep default checks offline with synthetic cases and permitted recorded files;
record live capture results separately. Preserve all original golden values.

| Delivery | Required evidence |
| --- | --- |
| M00 source decision | Verified fund roster, terms/use findings, two distinct dated samples, measured schema/weights, and open blockers |
| M04 acquisition PR | Allowed/denied redirects, timeout/429/5xx bounds, truncated/oversized/compressed files, HTML masquerading as data, crash before object commit, hash dedupe with distinct observations, and credential-safe metadata tests |
| M05 parser PR | Both actual fixtures parse; schema/section drift fails; date/units/decimals/provenance survive; missing identifiers/weights, negative/unsupported rows, explicit cash, residual boundaries, and same-date corrections are covered |
| Metadata-only XLSX repeat | A changed raw hash with identical worksheet/sharedStrings and date creates a new observation, not a second portfolio date or financial revision; M04 archives bytes, M05 compares canonical financial payload, M07 preserves the appropriate publication history |
| Subsequent milestones | M06 reviewed identity/taxonomy mappings; M07 atomic publication and knowledge-cutoff readers; M08 pinned replay; M11 scheduling/freshness |

M04/M05 produce archived evidence and assessed candidates. They must not update
the current published dataset or silently replace accepted holdings. Publication
concurrency, crash safety, accepted amendment order, and historical-as-known
queries belong to M07. No ingestion command, recurring job, production access,
or customer-visible source coverage is claimed implemented by this plan.
