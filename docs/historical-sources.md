# Historical holdings source assessment

Updated 7 November 2026. **No source yet satisfies the historical coverage gate.**
The user requires actual daily portfolio holdings for at least three years, or
since documented fund inception for newer ETFs. Historical source feasibility
now precedes the first importer decision. Two recent files demonstrate format
variation; they do not establish a historical archive.

The expandable [historical source mapping](../config/historical_sources.json)
records candidates, evidence states and unanswered questions. It complements the
[issuer register](source-register.md), which retains inspected documents and
source samples. Neither mapping enables production acquisition.

## Recommended investigation order

Investigate issuer archives and ETF Global first, then compare FactSet and
Morningstar. Include Intrinio as an API alternative if its actual offering meets
the same history requirement. A combination of vendor backfill and direct issuer
daily files is a candidate design, subject to demonstrated compatibility and cost.
Do not select that combination until the same-date comparisons pass.

The commercial links below are research starting points from general knowledge,
not live-verified product documentation. No specific vendor's daily holdings
coverage, earliest date, price, terms or suitability has been verified.

| Candidate | Why investigate | Evidence needed before selection |
| --- | --- | --- |
| [JPMorgan](https://am.jpmorgan.com/) issuer archive or historical delivery | Primary provenance; actual daily JGRO files already inspected | A separately evidenced archive/delivery route and complete per-fund date inventory. The inspected historical endpoint's empty holdings fields do not rule out another delivery route. |
| [Avantis](https://www.avantisinvestors.com/) issuer archive or historical delivery | Primary provenance; official daily disclosure and current complete-holdings route inspected | Older actual daily portfolios, fund/date inventory and original weights. The verified client CSV export does not itself provide older dates or extra precision. |
| [ETF Global](https://www.etfg.com/) | Specialist ETF-data candidate | Exact product, underlying sources, complete portfolios versus baskets, daily historical payloads and coverage for our funds |
| [FactSet](https://www.factset.com/) / [developer documentation](https://developer.factset.com/) | Institutional data-provider candidate | Identify the specific ETF dataset; distinguish daily portfolios from periodic fund-holdings or ownership products; obtain fund/date evidence and quote |
| [Morningstar](https://www.morningstar.com/business) | Fund-data provider candidate | Establish actual portfolio frequency for each ETF, historical depth, revisions and delivery. A daily database refresh does not establish a new portfolio every day. |
| [Intrinio](https://intrinio.com/) / [documentation](https://docs.intrinio.com/) | API-provider candidate | Prove an endpoint returns older complete portfolios by portfolio date, rather than latest holdings or historical prices; identify underlying supplier, costs and use conditions |
| [SEC EDGAR](https://www.sec.gov/edgar) / Form N-PORT | Regulatory source to evaluate for independent periodic comparisons | Verify current reporting/publication rules and exact fund filings. Periodic reports cannot supply missing daily observations; N-PORT ingestion remains deferred. |

An issuer download may remain the best route for ongoing daily acquisition even
if a vendor provides the backfill. Conversely, a vendor may offer both. Neither
route removes identity, denominator, unsupported-position or per-use review.

## What the inspected evidence establishes

JGRO has actual portfolios dated **5 and 6 November 2026**, captured prospectively.
The issuer's checked history response contains daily NAV/prices reaching 2022,
but `historicalHoldings` and `holdingAvailableDates` are null. That is a finding
about this route, not proof that JPMorgan lacks an archive elsewhere.

AVUS, AVUV and AVTM samples cover **5 November 2026**. The AVUS product page and
All Holdings page contain the same dated portfolio. Neither two page locations
nor a client-generated export adds another date. See the [JPMorgan report](jpmorgan-source-validation.md)
and [issuer assessment](issuer-assessment.md) for the underlying evidence.

No commercial historical payload or SEC filing has been inspected in this review.
No provider has been contacted and no current price or permission is assumed.

## Evidence required before choosing a source

The horizon ends on the **latest expected portfolio date**, using the documented
fund calendar and publication deadline. It does not end on whichever stale date
the provider happens to return. Obtain all expected dates in the preceding three
calendar years, or from documented inception if later. Record the actual start,
end, expected count, available count, missing dates and explanation per fund.
Do not substitute 756 assumed trading days for a verified calendar.

M00 establishes feasible delivery with a complete date inventory and representative
files. Full-history acquisition and reconciliation follow implementation, before
pilot sign-off. This avoids requiring an unbuilt importer to finish M00 while
preventing a small sample from being mistaken for demonstrated full delivery.

| Check | Required evidence |
| --- | --- |
| Exact funds and dates | Provider identifiers mapped to the proposed 10–25 fund roster; inception evidence; dated inventory across the entire required horizon; explicit gaps |
| Actual portfolios | Full constituent records including cash and unsupported positions; no top-ten lists, pricing baskets, proxy portfolios or price-based reconstructions presented as actual holdings |
| Historical samples | Files near the beginning of the required horizon, an intermediate year and recently, plus a consecutive daily window; fund/date identity must be inside the payload or evidenced contract |
| Independent comparison | Compare actual same-date holdings to inspected issuer disclosures. Explain missing/extra positions, identifier mappings, denominators, weights, quantities and precision; never normalize away differences. |
| Revisions and timestamps | Portfolio date, evidenced publication/vendor observation times, correction ordering and original versus restated history; identify any estimates or forward-filled values |
| Identifiers and scope | Stable fund and security identity, share-class changes, mergers/closures, and unsupported historical positions. Do not splice predecessor funds into a three-year record without a reviewed continuity basis. |
| Access and practical delivery | Backfill export/API, ongoing acquisition, limits, response sizes, retention and correction delivery; reproducible provenance for each file |
| Intended use and cost | Evidence for retrieval, storage, factual display and derived analytics; original-document and identifier rights where applicable; retention after cancellation; one-off backfill and recurring quote |

As a bounded initial exercise, request a complete date inventory and inspect
20 consecutive expected daily portfolios plus dates near three years ago,
two years ago, one year ago and the latest issuer comparison date. Use JGRO,
AVUS and AVUV as discovery probes because their identities/current disclosures
are already inspected; they are **not an admitted launch roster**. If a fund is
newer, start at its evidenced inception. Extend sampling when gaps, revisions or
layout changes appear. These sample sizes are investigation choices, not a claim
that passing them proves every historical record correct.

For source selection, require coverage evidence for every proposed launch fund,
not just these probes. Before pilot sign-off, reconcile the full acquired history
against the inventory and independently report missing source dates, rejected
snapshots, unresolved mappings and suppressed metrics. Today's eligible positions
do not establish eligibility on every historical date. A source gap cannot be
repaired by silently carrying a portfolio forward or reducing the agreed horizon.

The recurring target is **under US$1,500/month for the whole platform**, including
data. A quote must leave room for hosting and other services. Vendor research does
not authorize expenditure, acceptance of an agreement or external contact.

## Preserve the meaning of history

Backfill supports retrospective portfolio comparison using historical disclosures.
It does not establish what this system knew at the time: `first_observed_at` remains
the actual acquisition time, and publication to our catalog occurs later. Source
publication timestamps require evidence. The separate source-publication-time
research mode remains outside the current contract; do not advertise an as-known
backtest merely because portfolio dates are old.

Historical coverage for today's chosen funds is not a survivorship-free history
of the ETF market. Record closed/merged-fund coverage and the universe-selection
basis before making such a claim. Future metrics must also distinguish a reported
holdings change from an inferred trade.

If backfill and ongoing files come from different sources, test overlapping dates
and document differences in portfolio timing, revisions, identities and weights.
Retain each source's provenance. Do not silently substitute or merge conflicting
portfolios, or create an activity signal at the source transition.

## Current access and next evidence

The enforced environment policy permits the previously reviewed issuer hosts.
It currently excludes the SEC and commercial research hosts above. Seven exact
hosts were added to the saved draft while preserving existing settings:
`www.sec.gov`, `www.etfg.com`, `www.factset.com`, `developer.factset.com`,
`www.morningstar.com`, `intrinio.com` and `docs.intrinio.com`.
The configuration tool returned `requires_publish: true`. User review/save and
publication are pending; saving the proposal did not enable live access.

After activation, verify public product documentation and actual endpoint semantics
first. Record source URL, retrieval time, short supporting excerpts and document
hashes in the mapping. Mark provider claims separately from sample validation.
If a trial, quote or non-public archive is needed, prepare the exact request for
user review before contacting the provider or accepting terms. Until then the
source decision remains open and M04/M05 stay dependent on M00.
