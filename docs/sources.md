# Source feasibility register — M00

Latest assessment: 6 November 2026 (UTC). Initial access investigation: 1 November 2026.

Status: **incomplete — issuer access is blocked by the current environment network policy.**

This register implements the evidence-recording part of M00 in
[the MVP specification](spec.md). It does not approve an issuer, a fund roster,
commercial use, or a source adapter. No issuer holdings files have been downloaded
or added to fixtures.

## 6 November 2026 — expandable issuer review

The preferred acquisition route is now official issuer downloads. The research
sample includes Capital Group, Avantis, Dimensional, T. Rowe Price, Fidelity, and
JPMorgan Asset Management; this expands investigation, not the approved universe.

- [Canonical issuer mapping](../config/issuer_sources.json): separate access,
  terms, holdings, evidence, and admission states for each candidate.
- [Spreadsheet summary](issuer-sources.csv): generated from the mapping.
- [Review guide and candidate comparison](source-register.md): evidence fields,
  per-use terms review, sample measurements, and how to extend the mapping.
- [Importer implementation plan](importer-plan.md): source-validation gates,
  bounded retrieval, original-file storage, parsing, and acceptance tests.

The current runtime policy was rechecked on 6 November and still permits none of
the six discovery hosts. No blocked issuer request was retried, and no terms or
holdings files were obtained. All six have terms=not_reviewed and holdings=
not_measured; discovery URLs/tickers are leads rather than verified endpoints or
eligible funds. The mapping contains no invented file schemas or quality scores.

The environment draft now preserves the original issuer and GitHub API entries
and adds www.dimensional.com, www.troweprice.com, www.fidelity.com, and
am.jpmorgan.com. The save was confirmed; runtime activation remains outstanding.
These additions do not authorize commercial use or approve an issuer.

## Candidate investigation order

The initial two candidates below remain first in the expanded research order.

| Candidate | Initial discovery URL | Verified holdings endpoint | Launch roster |
| --- | --- | --- | --- |
| Capital Group | https://www.capitalgroup.com/ | Not established | Not selected |
| Avantis Investors | https://www.avantisinvestors.com/ | Not established | Not selected |

These are candidate issuer homepages for discovery, not validated daily holdings
endpoints. Availability, redirects, terms, fund coverage, and publication schedules
remain unverified.

## Observed access evidence

At the time of the access checks, the running managed environment reported a
restricted, enforced HTTP policy with no custom allowed hosts. The package-manager
preset does not include either candidate hostname.

| Check | Observed result | What it establishes |
| --- | --- | --- |
| Ordinary sandbox HEAD requests to the two candidate HTTPS homepages | curl exit 7: could not connect to the configured proxy | No issuer response was obtained |
| Narrowly scoped escalation for those same read-only requests | Automatic approval review rejected execution because both destinations are outside the enforced allowlist; escalation would bypass network policy | Further access requires the supported network-configuration workflow |

The issuer servers did not return these failures. They do not establish that a
website is unavailable, that an account is required, or that a source prohibits
retrieval. No direct connection, alternate mirror, or other policy bypass was
attempted.

The supported configuration tool subsequently confirmed a saved draft containing
these initial network additions, while preserving the selected presets:

- www.capitalgroup.com
- www.avantisinvestors.com

The save returned status=saved and requires_publish=true. This persists the
desired configuration; it does not change the currently enforced runtime policy.
The user needs to review and save the changes in environment settings, then
publish the environment through the supported workflow. The agent has not
published anything.

No network retry was made after the draft save. Recheck the enforced policy and
then the affected requests after the configuration is activated. Discover and
review any actual redirected or download host before requesting an additional
exact hostname; do not add wildcard domains speculatively.

## Unresolved source contracts

Neither candidate has passed the following checks:

| Required evidence | Current status | Acceptance before source integration |
| --- | --- | --- |
| Authoritative full-holdings endpoint | Unknown | Obtain endpoint from issuer material and confirm it represents the complete disclosed portfolio |
| Exact eligible fund identifiers | Unknown | Name at least ten eligible funds for the pilot; record issuer identifiers and verified tickers |
| Investment and instrument scope | Unknown | Confirm actual sampled positions fit the long-only equity/ADR/USD-cash contract |
| Portfolio date and publication metadata | Unknown | Identify portfolio date, any evidenced publication time, and first observation time independently |
| Publication calendar and deadline | Unknown | Record fund-level timezone, expected market dates, holidays and observed/contractual publication window |
| Schema and source identifiers | Unknown | Record columns, units, stable identifier fields, missing-value behavior and source row references |
| Weight denominator and precision | Unknown | Establish the reported denominator and decimal precision without assuming weights are independently reconciled |
| Total weights and metric eligibility | Not measured | Measure each sample's total and residual; report whether full overlap/active share meet the unit-total requirement |
| Completeness and schema-drift checks | Not designed against live files | Verify missing sections/columns and truncated files cannot become eligible snapshots |
| Access terms and rate limits | Not reviewed | Record authoritative terms and applicable download limits with URL and review date |
| Retention, display and commercial-use rights | Not reviewed | Document evidence and owner review before customer-facing use |
| Redistribution rights | Not reviewed | Do not enable bulk redistribution; MVP access does not grant feed rights |
| Two dated first-issuer samples | Not obtained | Capture two permitted, distinct portfolio dates with exact bytes and metadata |

No source is labeled approved merely because it can be fetched without
authentication. Identifier and classification data require their own rights and
provenance review.

## Evidence to capture when access becomes available

For each selected fund, record:

1. Issuer, fund name, stable issuer fund identifier, ticker and eligibility reason.
2. The issuer page linking to the download; exact document URL; actual redirect
   chain and allowed destination hosts.
3. Portfolio date, source timezone, retrieval timestamp in UTC, and any
   independently evidenced publication timestamp.
4. File type, content hash, byte length, schema fields, source identifiers and
   full-portfolio scope.
5. Reported weight basis, precision, row count, supported instrument categories,
   total weight, residual and identity/classification coverage.
6. Whether both source samples support full overlap/active share. If not, record
   the proposed known-matched-weight presentation or a separately reviewed
   methodology decision; do not normalize weights silently.
7. Applicable terms, rights evidence, review date, owner and permitted uses.
8. Expected publication calendar/deadline and the evidence distinguishing a
   source delay from a fetch or parsing failure.

Only permitted samples belong under tests/recorded. Preserve retrieval metadata
beside them, redact credentials if present, and keep test runs offline. A
synthetic example is not a substitute for the two required dated source samples.

## M00 completion and independent work

M00 remains open until the exact launch roster, first-source contract, rights
status, measured metric eligibility and two permitted dated samples are recorded.
Unresolved commercial permissions remain explicit pilot blockers even if
technical access succeeds.

M01–M03 may proceed with synthetic fixtures under the specification's dependency
rules. Source integration must not claim that this register establishes live
coverage or approval.
