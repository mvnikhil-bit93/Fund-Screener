# JPMorgan source validation — updated 7 November 2026

**The download route works, and identified money-market fund units are now in
scope following user approval on 7 November.** The 31-fund screen remains research
evidence, with no source admitted: actual fund/share-class identities, other
instrument mappings and source contracts still need verification. Approval of
an asset category does not approve every issuer row carrying a money-market label.

The [structured validation mapping](../config/jpmorgan_source_validation.json)
contains all fund identities, measurements, source references and proposals. It
extends the [issuer register](../config/issuer_sources.json); it is not runtime
configuration or an approved roster. Original files and constituent rows remain
outside Git. The [importer plan](importer-plan.md) remains conditional on M00.

## 1. Second portfolio date and revision behavior

**The second daily date is now obtained.** On 7 November at 13:30:41 UTC, the
official current download returned a workbook internally dated **6 November
2026**. Its date, 140 positions and both weight totals match the fresh product
JSON. The 17-column layout is unchanged from the 5 November file.

| Portfolio date | Positions | Market-value weight total | Net-assets weight total | Negative value/quantity rows |
| --- | ---: | ---: | ---: | ---: |
| 5 November | 140 | 100.00% | 100.06% | 1 |
| 6 November | 140 | 100.03% | 100.05% | 0 |

These are two prospectively captured daily source files, not an established
archive or two accepted analytical snapshots. The earlier negative-cash finding
belongs to 5 November; it is not carried forward into the 6 November sample.
Both dates retain the unresolved identity, denominator and source-use questions.

On 6 November, JGRO's official XLSX was retrieved again at **21:39:47 UTC**. Its
internal portfolio date remained **5 November 2026**. The file hash changed from
3c68e5376bb4… to 2914192f48a0…, but every uncompressed ZIP member except document
properties is byte-identical. Worksheet, shared strings, all 140 positions, dates
and notices are unchanged; ZIP timestamps also changed.

Record this as a separate acquisition observation, not a second portfolio date
or financial correction. M04 must retain the original bytes and observation;
M05/M07 must distinguish raw-file changes from changes in the financial snapshot.
A raw-hash change alone must not produce a holdings-change alert.

The fresh 7 November historicalData response makes the history distinction
concrete:

| History type | Observed response |
| --- | --- |
| Daily NAV/market-price history | 1,067 observations from 9 August 2022 through 6 November 2026 |
| Daily closing-price history | 1,068 observations from 8 August 2022 through 6 November 2026 |
| Constituent portfolio history | historicalHoldings and holdingAvailableDates remain null |

The inspected daily-download control exposes no date parameter, and generic
pricing-basket history is not enabled for JGRO. Daily publication does not establish
a public archive of old constituent portfolios. The issuer or a provider may
retain earlier daily holdings; their availability has not been established here.
Quarterly/annual reports are separate historical portfolio sources, not daily
holdings history. No paid licence is assumed necessary for an unverified archive.

The earlier gap arose because both 6 November checks saw the same latest portfolio
date and the checked history route offered no earlier holdings dates. The file
advanced by the 7 November check, supplying the second date. Exact publication
time remains unknown. No date was invented or recurring job installed.

## 2. Complete active-equity directory screen

The official US directory contains 78 ETFs: 25 passive and 53 active. Of the
active funds, 31 are equity funds: 20 U.S. Equity, nine International Equity and
two Global Equity. All report USD as fund currency. All 31 public product JSON
holdings datasets were inspected for the same 5 November date. This is not a claim
that 31 workbooks were downloaded; only JGRO has a directly inspected workbook.

| Screen | Count | Finding |
| --- | ---: | --- |
| Options or equity-linked-note strategies | 8 | HELO, HEQQ, HOLA, JEPI, JEPQ, JOYT, ROCQ, ROCY |
| Explicit short strategy | 1 | JLVP |
| Additional funds with observed equity-index futures | 4 | JMEE, JUSA, SCDS, MCDS |
| No observed derivative/short exclusion in this review | 18 | Candidates for further scope review, not proof derivatives can never occur |
| Money-market investments | 31 | One in every screened fund; none silently relabeled Cash |
| International/Global funds with non-USD cash | 11 | Fund USD reporting does not make each cash balance USD |
| Funds admitted under the current complete contract | 0 | No ten-fund roster established |

Foreign-equity trading currency is not itself an exclusion: the relevant cash
balances, instrument types and reporting basis are recorded separately. Source
codes such as CCC and USQ remain unresolved rather than being asserted to be
verified currencies. A REIT label is not automatically a derivative or proof of
supported ordinary equity; instrument evidence is needed.

The narrowest structural research set is below. These five have no observed
option/short/futures exclusion, negative value/weight, non-USD cash or unresolved
cash currency code. They still need money-market fund/share-class identity
verification, REIT/ADR mapping, source-use review, a denominator contract and
second-date evidence for the particular candidate fund.

Across these five, the money-market rows appear to describe two fund instruments,
but truncated descriptions and unverified source IDs do not establish the exact
fund/share-class identities. Those identities must be verified before the newly
supported category could admit them.

| Fund | Positions | Money-market % of net assets | Reported net-assets total | Other identity work |
| --- | ---: | ---: | ---: | --- |
| JAVA | 152 | 1.62% | 99.94% | 9 REIT, 1 ADR |
| JPEF | 42 | 2.01% | 100.02% | 1 REIT |
| LGDS | 106 | 0.1% | 100.01% | 2 REIT, 2 ADR |
| LVDS | 134 | 0.56% | 100.02% | 7 REIT |
| JPSV | 117 | 2.92% | 99.94% | 12 REIT |

Every net-assets total in this set differs from 100%. Even after other source
and scope decisions, current rules would suppress full overlap/active share for
these snapshots. A limited known-matched-weight output may be usable only after
its other eligibility requirements are met. LGDS's market-value total is 100%,
but that does not justify changing the chosen comparison denominator.

## 3. Weight definitions and cash

Retain both **% of Market Value** and **% of Net Assets**, with original precision.
The proposed primary analytical basis is the source-reported net-assets column,
subject to resolving its semantics and cross-fund comparability. This proposal
has not been adopted; no source weights are replaced with our calculations.

JGRO's issuer page defines NAV as assets less liabilities divided by shares.
The top-ten display has its own exclusions, including cash and money-market
positions. Those display exclusions do not remove rows from All Holdings.

For 5 November, signed holding values total **$8,931,616,484.87**. The same-date
public assets reference is **$8,937,110,909.07**, consistent with NAV × shares to
$0.015 at published precision. Their ratio is **99.938521%**, while reported
net-assets weights sum to **100.06%**. Twelve rows would fall outside ordinary
nearest 0.01-percentage-point rounding if that public reference were used as
their denominator. That rounding method is an assumption, not a verified issuer
rule. This is a reconciliation question, not proof of missing holdings or a
source error; timing, denominator and accounting treatment remain unresolved.

No difference is invented as cash. Negative cash retains its signed quantity
and value even if its displayed weight is zero. Its cause is not established:
we do not assert unsettled transactions, borrowing or an error. A negative cash
balance alone also does not prove a short-equity investment strategy.

## 4. Access, reuse and remaining source evidence

The public fund-specific download succeeds without a login or consent challenge.
No express automation prohibition was found in the reviewed JPMorgan terms, and
no paid-licence requirement for factual holdings was established. The validation
mapping separates recurring retrieval, factual analysis/customer tables, original
workbook retention, raw redistribution and reference/classification fields.
These remain scoped use-basis findings; public access is not blanket permission
to redistribute the branded workbook.

Exact publication timezone, holiday calendar, deadline and correction policy
remain unverified. A closing-price notice saying 4 PM is not a holdings deadline.
The official prospectus URL returns an HTML wrapper pointing to
connect.rightprospectus.com. That exact host has been added to environment draft
revision 5, preserving earlier settings; it is not active and the embedded
prospectus has not been read. No environment was published.

## 5. Approved scope extension — 7 November 2026

The user approved support for **explicitly identified money-market fund share
classes as direct securities**. The specification and candidate data contract
now implement the distinct money_market_fund category:

- Preserve each fund/share-class identity, units, market value and reported weight.
- Keep these investments distinct from explicit cash; no look-through, assumed
  par valuation or automatic matching between different money-market funds.
- Match overlap only for the same confidently identified instrument. They remain
  non-cash securities under the current concentration definition.
- Leave unreviewed sector/domicile mappings Unclassified. Do not infer a sector
  from the fund sponsor or automatically adopt issuer classifications.
- Keep signed-negative-cash support, foreign-currency cash, derivatives and relaxed
  numerical tolerances outside this extension. Preserve every excluded row as evidence.

The five funds above remain candidates for further validation. The extension does
not admit them, create a ten-fund roster, or resolve identity, per-fund second-date,
denominator or use-basis gaps. Their exact money-market instruments still need
identification rather than automatic conversion from the source label.

The [specification](spec.md#launch-universe) records the approved amendment.
Representation tests cover distinct share classes and cash, JSON/Arrow/canonical
round trips, signed candidate evidence, decimal precision and identity requirements.
Existing golden values, old-record hashes and financial eligibility gates remain
unchanged. Overlap, concentration and source-admission engines are later work.

## 6. Follow-up work and acceptance evidence

| Item | Work | Completion evidence |
| --- | --- | --- |
| M00-JPM-01 | Second daily portfolio date | Captured JGRO files for 5 and 6 November with internal dates and source confirmation; analytical acceptance remains separate |
| M00-JPM-02 | Reported weight basis and schedule | Document denominator/timing and publication calendar; retain unresolved diagnostic differences |
| M00-JPM-03 | Money-market scope extension | Approved 7 November; specification and candidate representation implemented and tested. Actual instrument verification remains open. |
| M00-JPM-04 | Exact eligible roster and identities | Fund/date-specific position checks and reviewed ADR/REIT/reference IDs; ten-fund target remains unchanged |
| M00-JPM-05 | Operation-specific use basis | Document retrieval, factual use and original-file retention separately; clarify only material unresolved conditions |
| M00-JPM-06 | Daily historical archive — open, prerequisite to adapter selection | Evidence a three-year/since-inception route, per-fund date inventory and historical samples; compare an issuer archive or alternative provider under the [historical-source gate](historical-sources.md). Two recent JGRO files do not meet this requirement. |
| M04/M05/M07 | Raw versus financial revisions | Metadata-only XLSX change archives a new observation without inventing a new portfolio date or financial correction |

This update advances M00 research and the approved candidate-model extension.
No live production importer, parser, recurring job, financial engine or
customer-visible dataset is claimed implemented.
