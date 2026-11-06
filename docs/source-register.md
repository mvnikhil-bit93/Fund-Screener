# Issuer source register

Assessment date: 6 November 2026. Preferred route: official issuer downloads.

The [JSON register](../config/issuer_sources.json) is the canonical, expandable
research mapping. The [CSV summary](issuer-sources.csv) opens in a spreadsheet.
The [importer plan](importer-plan.md) describes the work after source validation.
The register's schema_version identifies this research format, not the canonical
ledger-record schema or a financial methodology version.

**Live assessment is now underway.** The replacement environment permits all six
issuer discovery hosts. The [live assessment](issuer-assessment.md) records terms
or policy evidence for all six issuers, including the limited scope of Capital
Group's policy review. Avantis product pages and its All Holdings route were
inspected, along with one directly downloaded JPMorgan JGRO workbook. All sampled
portfolios are dated 5 November 2026. Avantis's accompanying notice describes
publication of each position's identity and quantity every business day before
trading. This supports an issuer-declared daily disclosure; it does not establish
independently reconciled completeness, delivery reliability, a second portfolio
date, production-use approval, or an approved launch roster.

## Investigation sample

Priority is an investigation order, not a measured quality or licensing score.
Capital Group and Avantis remain the original first two candidates; the other
four extend the research sample at the user's request. Initial seed tickers were
discovery leads from prior knowledge. AVUS, AVUV and JGRO product identities have
been verified through official catalogs/product pages; their portfolio
eligibility remains unresolved. Other seeds retain their recorded evidence state.

| Priority | Issuer and discovery homepage | Discovery tickers | Main question to resolve |
| --- | --- | --- | --- |
| 1 | [Capital Group](https://www.capitalgroup.com/) | CGUS, CGDV | Can complete, dated files support enough eligible funds for the pilot? |
| 2 | [Avantis Investors](https://www.avantisinvestors.com/) | AVUS, AVUV | What denominator, precision, identifiers, and instrument types occur in the files? |
| 3 | [Dimensional](https://www.dimensional.com/) | DFAU, DFAC | What is the full-holdings delivery method, including cash and unsupported positions? |
| 4 | [T. Rowe Price](https://www.troweprice.com/) | TCAF | Does each chosen product disclose its complete actual portfolio rather than a proxy? |
| 5 | [Fidelity](https://www.fidelity.com/) | FELC | Is the file the right ETF and market, with complete dated holdings? |
| 6 | [JPMorgan Asset Management](https://am.jpmorgan.com/) | JGRO | Does the particular strategy avoid option overlays and other unsupported instruments? |

The questions are hypotheses to test, not findings that an issuer has a defect.
Do not select every fund from an issuer merely because one sampled fund passes.
The six issuers and nine seed tickers are not the target 10–25-fund pilot roster.

## Access and evidence status

The JSON preserves the earlier blocked-policy evidence separately from the
replacement environment's active policy and live observations. All six sites
now return public responses; access gates and permissions remain source-specific.
Capital Group's linked advisor composites route redirected to authentication,
and Fidelity's homepage presented an international-use agreement. Neither gate
was accepted or bypassed; neither observation proves all issuer routes are gated.

The published network settings include the six discovery hosts and api.github.com.
The new draft preserves them and restores the earlier setup/start instructions.
It additionally proposes avantisinvestors.prospectus-express.com after the
official Avantis catalog linked quarterly holdings documents there. That new
host remains inactive until the user reviews/saves and publishes the draft.
The observed res.avantisinvestors.com factsheet host has not been requested or
added; a factsheet is not assumed to be complete holdings.

The draft now also includes www.ecfr.gov to verify the current Rule 6c-11 text.
This addition remains inactive; the issuer's daily-disclosure statements are
recorded independently of unverified fund-specific reliance on that rule.

Verify the active policy before requesting a newly approved host. Record actual
redirects and investigate the applicable document terms; discovery of a URL is
not a commercial licence. No unknown destination is followed automatically.

## Extending the mapping

Edit config/issuer_sources.json, then regenerate the spreadsheet summary:

```sh
python scripts/export_issuer_sources.py
python scripts/export_issuer_sources.py --check
```

Do not edit the generated CSV independently. The exporter only formats research
data; it does not validate source approval or authorize an importer. Production
configuration validation is planned in M04. No runtime currently consumes this
register, and changing a boolean does not make an endpoint safe or licensed.

Use stable IDs to join records. Keep unknown URLs, dates, measurements, and
decisions null; use empty arrays when no evidence exists. Unknown is never zero,
"permitted," or an assertion that no restriction exists. Add evidence records
only after obtaining the corresponding material; do not add placeholder samples
to increase counts. Retain old reviews and mark what supersedes them.

Only credential-safe URLs belong in the register, CSV, or Git. Redact tokens and
other credential-bearing query parameters/fragments from signed download and
redirect URLs, record that redaction occurred, and never store cookies or full
authorization headers here. Retain exact secret-bearing request evidence only
in appropriately restricted storage when necessary and permitted. A redacted
provenance URL is not a fetchable endpoint or a substitute for a refresh mechanism.

| Collection | One record represents | Fields to record; unknowns remain explicit |
| --- | --- | --- |
| issuers | A candidate organization and current assessment summary | Stable issuer_id, discovery lead, review status, linked records, questions and decision |
| terms_documents | A particular version of a terms document | document_id, issuer_id, exact source_url, applicable fund_ids or explicit issuer-wide scope, retrieved_at UTC, effective date if stated, content_sha256, relevant clauses/excerpts, storage permission/path, reviewer and reviewed_at |
| disclosure_evidence | One source page, download-control script, or public catalog supporting discovery | evidence_id, issuer_id, source_url, fetched_at, SHA-256, byte length, artifact kind and exact limited finding; no executable script or constituent data in Git |
| disclosure_routes | One fund's observed delivery route | route_id, fund_id, official_url, delivery mechanism, coverage claim versus measured completeness, supporting evidence/sample IDs, specific terms applicability and unresolved use basis |
| field_usage_profiles | One proposed material category | Factual observations, identifier strings/services, classifications/enrichment, or protected original artifacts; intended treatment and unresolved basis |
| rights_decisions | One reviewed use for a specific scope | decision_id, issuer_id, fund_ids or explicit issuer-wide scope, use, status, evidence and exact clause references, conditions, reviewer, reviewed_at, expiry/review date if applicable, supersedes_decision_id when updated; distinguish a licence grant from another documented lawful-use basis and unresolved applicability |
| funds | One fund identity and source-contract assessment | fund_id, source_id, issuer_id, issuer_fund_id, verified ticker/exchange/name/currency, strategy and transparency evidence, fund page, holdings endpoint, verified hosts, rights review references, file/schema/calendar versions, admission decision |
| samples | One exact file received for a fund | sample_id, fund_id, source_id, exact URL and redirect chain, fetched_at UTC, evidenced publication time, portfolio date, SHA-256, bytes, MIME/format, permitted storage path, field_mapping_id and quality measurements |
| field_mappings | One versioned, observed file layout | mapping_id, source_id, version, supporting sample_ids, encoding, delimiter or sheet, header/footer rules, raw columns/locations, target fields, units, date rules, denominator and completeness checks |

Fund records must carry their own effective terms assessment where restrictions
or permissions differ by fund or file. An issuer-level review does not grant
blanket permission to every product. Store reviewer decisions with their evidence
references and conditions; retain restricted/uncertain outcomes explicitly.
The permission strings in each issuer's terms_review are summaries only. Before
changing one from unknown, add a rights_decisions record for that exact use and
scope and link its ID in terms_review.decision_ids. Each permission needs its own
supporting evidence, conditions, reviewer, and date; a general document list is
not evidence that every use is permitted. A decision can rely on applicable
permission or another documented legal basis; an affirmative issuer licence is
not automatically necessary for every use of factual data. Future importer
validation must inspect these scoped decisions, not trust a summary string or
production-enabled flag.

## Terms review procedure

1. Locate the official fund's daily portfolio disclosure and its delivery route.
   Record the issuer's actual claims about positions covered, valuation date and
   publication frequency. Distinguish these claims from independent sample
   measurements. A marketing label, creation basket, proxy portfolio, or quarterly
   report does not establish complete daily disclosure. Record any applicable
   regulatory basis separately; do not assume every ETF uses the same regime.
2. Read the regional website terms, disclosure/file notices, provided-tool terms,
   and referenced data conditions. Record exact URLs, clause scope, and evidence
   versions. Check whether specific terms supersede general terms. Identify the
   actual access method and any authentication, consent, automation, audience,
   or rate restrictions. Public visibility does not override those conditions.
3. Separate factual portfolio observations from other material. Reported dates,
   quantities, values, weights, names and tickers are candidates for factual use;
   commentary, presentation, ratings, branded classifications and other additions
   require their own assessment. Identifiers and mappings need field-specific
   review. Under US copyright principles, facts generally are not protected as
   such; the surrounding expression or compilation may be. Contractual access
   conditions, third-party rights and other applicable law remain separate.
4. Assess each intended use separately: manual research download, automated
   retrieval, original-document retention, commercial internal analysis, customer
   display of factual holdings, derived analytics, raw redistribution, public
   Git fixtures, identifier reuse, and classification reuse. Record the relevant
   fields, endpoint, audience, and evidence for the decision. A protected-content
   clause is not automatically a finding that each underlying fact is protected.
5. Record unknown, permitted, conditional, or prohibited for the scoped use, with
   the reviewed basis and conditions. Distinguish an affirmative licence, a
   documented factual-use or statutory basis, and unresolved applicability.
   Silence establishes neither permission nor prohibition and does not prove a
   paid licence is required. A public download button supports route discovery;
   robots.txt concerns retrieval behavior. Neither alone decides all reuse rights.
6. Resolve only the uncertainty that affects the proposed operation. Check a
   provided tool or disclosure-specific route before concluding written permission
   is necessary. Respect explicit access restrictions while that investigation
   continues; do not bypass a gate. Escalate ambiguous material uses for Nikhil's
   review or a targeted permission inquiry. No external messages are sent here.
7. Keep research capture, recurring retrieval, document retention, factual-data
   use, and customer publication decisions separate. Do not publish original
   documents or constituent fixtures in Git without a reviewed basis for that
   operation. Unresolved material rights remain pilot blockers under the spec;
   permitted investigation can continue without asserting legal clearance.

This register records a practical evidence review; it does not replace a required
owner or legal decision on ambiguous commercial terms.

## Holdings sample review procedure

Obtain two permitted files for the same fund with **distinct portfolio dates**
from the first viable source. Two downloads of today's file do not count as two
dated samples. If a prior date is unavailable, keep the gap open until a later
publication; never invent an archive date or backdate observation time. Expand
inspection to every proposed launch fund before approving the roster.

For each sample, record:

- Exact download URL, verified redirect chain, retrieval time, file SHA-256 and
  size; retain only necessary safe response metadata such as ETag/Last-Modified,
  never cookies, credentials or full authorization headers.
- Issuer/fund identity and the portfolio date from evidence in the file or
  authoritative accompanying metadata. HTTP Last-Modified is not automatically
  the portfolio date or an evidenced publication timestamp.
- Format and raw layout: encoding, sheets, header/footer lines, exact column
  names, date formats, decimal precision, identifier namespaces and missing-value
  markers. Map what is actually present; do not invent standard issuer columns.
- Whether this is the complete actual portfolio, a top-holdings excerpt, proxy
  portfolio, creation basket, or another document. Preserve an issuer's statement
  that every position is disclosed as positive coverage evidence, separately
  from reconciliation, omitted sections, and numerical completeness. File type
  and a weight sum close to one do not establish completeness.
- Reported denominator and units. Preserve raw decimal weights and convert
  percentages to fractions explicitly. Record row count, sum of admitted weights
  W, signed residual 1-W, negative/missing weights, duplicates, identifier gaps,
  explicit cash, unsupported positions and any reconciliations.
- Separate source completeness, identity/classification coverage, supported
  asset eligibility, and metric eligibility. Follow spec section 8: unexplained
  absolute residual above 0.01 quarantines; an absolute residual above 1e-9
  prevents unit-total metrics. Never normalize or invent balancing cash.
- Expected publication calendar, timezone, deadline, corrections, and available
  historical dates, each with evidence. Mark unobserved schedules unknown.

Suggested sample quality object (shape only; this is not a measured sample):

```json
{
  "portfolio_date": null,
  "source_completeness": "unknown",
  "row_count": null,
  "weight_unit": null,
  "weight_denominator": null,
  "reported_precision": null,
  "admitted_weight_sum_decimal": null,
  "residual_decimal": null,
  "missing_weight_rows": null,
  "unsupported_position_rows": null,
  "identifier_coverage": null,
  "full_overlap_eligible": null,
  "quality_reasons": []
}
```

## Decision before implementing the first adapter

Prefer the first candidate with permitted research access, complete dated files,
an understood schema/denominator, sufficient eligible funds, and a workable use
path for the product. Record unresolved commercial rights as pilot blockers;
record a documented factual-use basis where supported rather than demanding an
issuer licence by default.
If rounding prevents full overlap, document the usable known-matched-weight
presentation without relaxing the methodology. No candidate currently passes
this evidence gate. M00 remains open; the importer plan is conditional on filling
the missing evidence, and no issuer-specific adapter has been implemented.
