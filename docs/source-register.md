# Issuer source register

Assessment date: 6 November 2026. Preferred route: official issuer downloads.

The [JSON register](../config/issuer_sources.json) is the canonical, expandable
research mapping. The [CSV summary](issuer-sources.csv) opens in a spreadsheet.
The [importer plan](importer-plan.md) describes the work after source validation.

**Live assessment is blocked.** The current environment's enforced policy permits
none of the six issuer discovery hosts. No terms pages or holdings files have
been retrieved in this review. There are zero verified download endpoints,
zero reviewed terms documents, zero measured samples, and no approved funds.
This is an investigation shortlist and evidence structure, not a completed
licensing review, quality assessment, or launch roster.

## Investigation sample

Priority is an investigation order, not a measured quality or licensing score.
Capital Group and Avantis remain the original first two candidates; the other
four extend the research sample at the user's request. Seed tickers are discovery
leads from prior knowledge. Current names, listings, strategy, and eligibility
must be established from issuer evidence before admitting a fund.

| Priority | Issuer and discovery homepage | Unverified seed tickers | Main question to resolve |
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

The latest runtime check and its interpretation are recorded under
network_evidence in the JSON. No blocked issuer request was retried or routed
through another host. This establishes an environment limitation; it says
nothing about issuer availability, authentication, terms, or file quality.

The environment draft contains the six exact discovery hosts above and preserves
the existing api.github.com entry. Four hosts were newly added: www.dimensional.com,
www.troweprice.com, www.fidelity.com, and am.jpmorgan.com. Saving does not enable
runtime access. The user must review/save the settings and publish the updated
environment through the supported workflow. The agent has not published it.

Recheck the runtime policy after activation. Verify each HTTP response, then
record redirects and request any additional exact download hostname only when
issuer evidence establishes it. Homepage access is not proof that the file host
is accessible. Do not follow redirects to unknown hosts automatically.

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

| Collection | One record represents | Required evidence when populated |
| --- | --- | --- |
| issuers | A candidate organization and current assessment summary | Stable issuer_id, discovery lead, review status, linked records, questions and decision |
| terms_documents | A particular version of a terms document | document_id, issuer_id, exact source_url, applicable fund_ids or explicit issuer-wide scope, retrieved_at UTC, effective date if stated, content_sha256, relevant clauses/excerpts, storage permission/path, reviewer and reviewed_at |
| rights_decisions | One reviewed use for a specific scope | decision_id, issuer_id, fund_ids or explicit issuer-wide scope, use, status, document_ids with exact clause references, conditions, reviewer, reviewed_at, expiry/review date if applicable, supersedes_decision_id when updated |
| funds | One verified ETF source contract | fund_id, source_id, issuer_id, issuer_fund_id, verified ticker/exchange/name/currency, strategy and transparency evidence, fund page, holdings endpoint, verified hosts, rights review references, file/schema/calendar versions, admission decision |
| samples | One exact file received for a fund | sample_id, fund_id, source_id, exact URL and redirect chain, fetched_at UTC, evidenced publication time, portfolio date, SHA-256, bytes, MIME/format, permitted storage path, field_mapping_id and quality measurements |
| field_mappings | One versioned, observed file layout | mapping_id, source_id, version, supporting sample_ids, encoding, delimiter or sheet, header/footer rules, raw columns/locations, target fields, units, date rules, denominator and completeness checks |

Fund records must carry their own effective terms assessment where restrictions
or permissions differ by fund or file. An issuer-level review does not grant
blanket permission to every product. Store reviewer decisions with their evidence
references and conditions; retain restricted/uncertain outcomes explicitly.
The permission strings in each issuer's terms_review are summaries only. Before
changing one from unknown, add a rights_decisions record for that exact use and
scope and link its ID in terms_review.decision_ids. Each permission needs its own
supporting clauses, conditions, reviewer, and date; a general document list is
not evidence that every use is permitted. Future importer validation must inspect
these scoped decisions, not trust a summary string or production-enabled flag.

## Terms review procedure

1. Start at the issuer's official fund page. Read the applicable regional website
   terms, download/file notices, and referenced data conditions. Record exact URLs
   and clauses with retrieval dates and hashes where retention is permitted.
2. Assess each intended use separately: manual research download, automated
   retrieval, raw-file retention, commercial internal analysis, customer display
   of holdings, customer display of derived analytics, raw redistribution,
   publication of fixtures in Git, identifier reuse, and classification reuse.
3. Record a status of unknown, permitted, conditional, or prohibited for each use,
   supported by document IDs, scope, conditions, and reviewer. Silence in a terms
   page remains unknown. robots.txt concerns retrieval behavior, not a grant of
   commercial rights. A public download button alone is insufficient evidence.
4. Track restrictions such as audience, attribution, retention period, automated
   request limits, and third-party data separately. Flag unclear terms for Nikhil's
   review or permission inquiry; no external messages are sent by this task.
5. Separate permitted research capture from approval for customer-facing use.
   Do not put downloaded files in public Git unless that specific use is cleared.
   When required permission is unresolved, record the blocker and avoid that use.

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
  portfolio, creation basket, or another document. File type and a weight sum
  close to one do not establish completeness.
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
path for the product. Record unresolved commercial permissions as pilot blockers.
If rounding prevents full overlap, document the usable known-matched-weight
presentation without relaxing the methodology. No candidate currently passes
this evidence gate. M00 remains open; the importer plan is conditional on filling
the missing evidence, and no issuer-specific adapter has been implemented.
