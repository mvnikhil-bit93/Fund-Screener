# Direct issuer assessment — 6 November 2026

The refined review supports continuing with direct issuer disclosures. **The
evidence does not establish that a paid data licence is needed for the underlying
holdings facts.** General website conditions, the acquisition method, factual
reuse, and proprietary additions need separate findings. Our earlier assessment
was too broad where it treated written consent as the necessary answer before
identifying the actual disclosure and material being used.

Two concrete routes are now verified: Avantis's official **All Holdings** page
and issuer-provided CSV export mechanism, and JPMorgan's directly downloadable
JGRO Excel holdings file. Avantis's pages describe daily disclosure of each
position. These findings improve the source evidence; they do not yet resolve
the second portfolio date, source contract, or fund eligibility. No source is
admitted for production.

The subsequent [JPMorgan validation](jpmorgan-source-validation.md) screens all
31 active equity funds in its US directory and records the current roster/scope
decision, repeat-download result and denominator diagnostics. The initial sample
measurements below remain valid; they do not establish an approved launch roster.
Its 7 November update records the approved money-market extension and a second
JGRO daily file dated 6 November. The original measurements below describe the
initial 5 November samples.

The [source register](../config/issuer_sources.json) holds structured findings
and provenance; its [spreadsheet view](issuer-sources.csv) summarizes status.
The [review guide](source-register.md) explains the evidence fields and the
[importer plan](importer-plan.md) sets out implementation after source admission.
Findings below are a preliminary evidence review, not a legal determination or
permission granted by the issuer. Full source pages and holdings remain outside
Git; the register records URLs, retrieval times, hashes, and limited findings.

## Issuer comparison

| Issuer | Terms or policy finding | Holdings/access finding | Next action |
| --- | --- | --- | --- |
| Capital Group | [Third-party conditions](https://www.capitalgroup.com/individual/trademarks.html) concern that material; they do not settle first-party holdings facts or every identifier string. | The [public listing](https://www.capitalgroup.com/individual/investments/returns?term=monthly) links an advisor composites route that requires authentication. That observation is limited to that route. | Locate a public daily disclosure and identify its actual fields and conditions. |
| Avantis Investors | [Main terms](https://www.avantisinvestors.com/avantis-terms-and-conditions/en-us/) include a limited view/use/download/print licence. No specific paid-licence requirement for factual holdings was found. Production access and factual-use basis still need scoped review. | AVUS has a verified All Holdings route with an issuer-provided client-side CSV export; three funds have dated holdings evidence. | Complete the source contract, factual-use review and second-date sample; resolve instrument and precision limits. |
| Dimensional | [US terms](https://www.dimensional.com/terms-of-use-us) restrict commercial website use. The repeated-access clause concerns conduct that could damage, disable or overburden the site and excepts issuer-provided tools. | No daily holdings route or sample was inspected. This is an evidence gap, not a finding that public holdings are unavailable. | Identify the official disclosure/tool and its specific conditions before deciding what authorization is needed. |
| T. Rowe Price | [US terms](https://www.troweprice.com/en/us/terms-of-use) explicitly restrict scraping. Section 1 lets section-specific terms govern conflicts; a separate Conduct clause refers to approved or issuer-provided tools. These clauses must be read together. | The [ETF reports page](https://www.troweprice.com/personal-investing/funds/etfs/prospectuses-reports.html) links TCAF; no holdings acquired. No disclosure-specific exception has been verified. | Keep acquisition on the restricted route disabled; establish a supported disclosure mechanism and its conditions. This does not establish a need to buy a data licence. |
| Fidelity | [Terms](https://www.fidelity.com/terms-of-use) restrict commercial website use and third-party automated access, while recognizing authorized/issuer-provided tools and section-specific terms. | The homepage's international-use agreement was not accepted. No FELC disclosure route verified; this does not prove all public ETF disclosures are gated. | Establish a legitimate disclosure route without bypassing the gate; assess access and factual reuse separately. |
| JPMorgan Asset Management | [US terms](https://am.jpmorgan.com/us/en/asset-management/per/terms-of-use/) address protected works and statutory exceptions. Factual tables or independently calculated metrics are not automatically protected-work reproduction. | The official JGRO Download All Holdings control returned an actual Excel workbook dated 5 November, with 140 positions and two distinct weight bases. | Resolve denominator choice, negative cash and money-market treatment, identifiers, factual-use basis and second-date coverage. |

The Capital Group [Account Agreement](https://www.capitalgroup.com/individual/account-agreement.html)
was also read. Its account-information accuracy disclaimer is not a holdings-file
licence or a measured finding that a particular portfolio file is inaccurate.
Likewise, issuer disclaimers about accuracy/completeness are not substitutes for
measuring actual files. JPMorgan's [site disclaimer](https://am.jpmorgan.com/us/en/asset-management/per/site-disclaimer/)
reinforces this distinction.

## What can be reused, and on what basis?

In the US, underlying facts generally are not protected by copyright. An issuer's
page or report can nevertheless contain protected writing, layout, and original
compilation features. Applicable contractual access/use conditions are a separate
question. Public disclosure is not an automatic open-data licence, and the absence
of a licence statement does not prove permission or payment is legally required.

| Material | Proposed importer treatment |
| --- | --- |
| Portfolio date, reported security identity, quantity, market value and weight | Core factual observations; preserve source meaning and precision, with a documented route and use basis. |
| Ticker, CUSIP, ISIN and SEDOL | Separate disclosed identifier strings from proprietary lookup databases or mapping services; assess the actual source/service. |
| Sector, country, ratings, index data and other enrichment | Identify provider and meaning; do not automatically adopt issuer labels as the product taxonomy or equate country with legal domicile. |
| Logos, commentary, charts and page/report presentation | Exclude from customer factual tables. Original-artifact retention for provenance has its own review, separate from redistribution. |

A source can be admitted on an appropriate documented basis without purchasing
a feed. Possible bases include an applicable grant, official delivery conditions,
or factual reuse with the relevant contract questions resolved. Internal source
approval is a project decision; it is not a licence issued by the data owner.

The regulatory reference to verify is [17 CFR 270.6c-11(b)(1)](https://www.ecfr.gov/current/title-17/chapter-II/part-270/section-270.6c-11).
The general framework concerns ETFs relying on that rule, not every ETF or every
nontransparent structure. Current rule text and each fund's reliance have **not**
been live verified here: www.ecfr.gov is outside the active network policy and
has been added to the environment draft. The Avantis findings below rely on its
own statements and observed pages, not an assumed fund-specific legal obligation.

## Measured Avantis evidence

The official [US catalog](https://www.avantisinvestors.com/avantis-investments/en-us/)
verified AVUS as Avantis U.S. Equity ETF, issuer fund 114, and AVUV as Avantis
U.S. Small Cap Value ETF, issuer fund 119. Its product routes led to dated
etfHoldings arrays. AVTM was linked directly from the issuer homepage. All three
arrays have a portfolio date of **5 November 2026**. Received HTML was retained
in private review storage and inspected without executing issuer JavaScript.

The product holdings disclosure states that Avantis publishes identities and
quantities of each position on each business day before trading, with securities
reported at market value. It also warns that presentation can differ from
regulatory schedules because of accounting/reporting requirements. Record this
as **issuer-declared daily position coverage**, separately from measured extraction
completeness, denominator reconciliation, numerical completeness and eligibility.

The issuer's View All Holdings control leads to the verified
[AVUS All Holdings page](https://www.avantisinvestors.com/avantis-investments/en-us/total-holdings/114/?type=etf).
Its All Holdings download control builds a CSV in the browser from the embedded
etfHoldings array. This is a real issuer-provided export mechanism, even though
there is no independently verified server CSV URL. The control was verified by
reading the issuer's code; no browser-generated CSV was captured. The verified
All Holdings page contains exactly the same 1,943 AVUS rows and field values as
the product-page sample, so the export adds no weight precision. The separate **Daily Pricing
Basket** download uses different data and must not be substituted for actual
portfolio holdings.

| Official product page | Issuer fund number | Rows | Raw displayed-weight sum | Arithmetic gap to 100% | Rows displaying 0.00% |
| --- | --- | --- | --- | --- | --- |
| [AVUS](https://www.avantisinvestors.com/avantis-investments/en-us/avantis-us-equity-etf/) | 114 | 1,943 | 99.19% | 0.81 percentage points | 819 |
| [AVUV](https://www.avantisinvestors.com/avantis-investments/en-us/avantis-us-small-cap-value-etf/) | 119 | 793 | 99.83% | 0.17 percentage points | 91 |
| [AVTM](https://www.avantisinvestors.com/avantis-investments/en-us/avantis-total-equity-markets-etf/) | 75 | 1,709 | 98.95% | 1.05 percentage points | 815 |

The measurements above come from product-page HTML captures. Weights are
percentage strings rounded to two decimal places; no missing or negative
displayed weights were observed. The raw sums include every displayed row and
are **not** admitted analytical W. The arithmetic gaps alone are not final
unexplained-residual or quarantine decisions: denominator, completeness, and
supported-position treatment remain unresolved. A displayed 0.00% does not
establish a truly zero position or a missing value.

AVUS includes a sweep investment vehicle, warrants, rights, and preferred stock;
AVUV includes a sweep vehicle and a right. Both remain unadmitted while these
positions and numerical eligibility are assessed. A sweep fund must not silently
be relabeled explicit USD cash, and rounded-zero unsupported rows must not be
dropped to pass a gate. AVTM additionally includes other funds and non-USD
currency evidence, making it a negative scope/quality case rather than an
approved MVP fund. Admitted W and full-overlap eligibility are not established
for any of the three.

Observed fields include name, ticker, securityType, CUSIP, ISIN, SEDOL,
shareQuantity, contractCount, baseMarketValue, weight, coupon, maturityDate,
sector, and country. Presence is not semantic approval: currency/denominator,
identifier continuity, taxonomy rights, and the meaning of country remain to be
verified. No sector label has been silently adopted as the product's taxonomy.

Three funds on one portfolio date do not establish two-date coverage, daily
reliability, or revision behavior. The official catalog links quarterly holdings
documents on avantisinvestors.prospectus-express.com and fact sheets on
res.avantisinvestors.com. These destinations were observed but not fetched because
they were outside the active network policy. Their contents, dates, and applicable
conditions remain unverified; fact sheets and quarterly reports do not establish
daily history. A second date must come from authoritative material or a later
permitted publication, not a repeat download of the same portfolio date.

## Measured JPMorgan evidence

The public issuer fund directory identifies JGRO as JPMorgan Active Growth ETF,
fund identifier 46654Q609, with USD reporting and active management metadata.
The product's Download All Holdings control returned an actual XLSX workbook
through the issuer's same-host FundsMarketingHandler endpoint. Its **Holdings**
sheet identifies the fund and contains an internal as-of date of **5 November
2026**, independently of the filename.

| Workbook observation | Result |
| --- | --- |
| Positions | 140, rows 9–148; header row 8 |
| Sum of reported % of Market Value | 100.00% |
| Sum of reported % of Net Assets | 100.06% |
| Displayed zero weights | Two rows in each weight column |
| Reported types | 137 domestic common stocks, one ADR, one money-market position, one currency position |
| Identifiers | Tickers; no position-level CUSIP/ISIN/SEDOL columns; cash ticker blank |

The currency position reports **negative USD market value and quantity**, while
both rounded weight fields display zero. The money-market position also requires
scope review. A raw total of 100% therefore does not establish eligibility or
justify selecting that denominator simply to make totals balance. Both reported
weight columns and source quantities/values must survive parsing; analytical W
remains unadmitted. No cash was invented, removed or relabeled.

The workbook includes sector, industry and country fields. These are separate
from the core numerical observations; their provider, taxonomy and country
meaning remain unverified. Its brief holdings-change and branding notices do not
establish an open-data licence, nor do they demonstrate that a paid licence for
the factual rows is necessary. The file, surrounding website conditions and
proposed access/use still need their scoped assessment. No constituent rows,
workbook bytes or logos are published in Git.

The initial review obtained one actual standalone holdings file, for one date.
The 7 November follow-up has since captured the next daily file. Sustained delivery
reliability, correction behavior and independent asset reconciliation remain
untested. The mapping records the exact endpoint, source/code evidence,
file hash, layout, both denominators and the measured limits.

## Consequences for the first importer

1. Record access conditions, factual-use basis and proprietary additions per
   route and operation. Do not default every factual field to a paid-licence or
   written-consent requirement. Actual unresolved source rights still block
   production admission; permitted research can continue. No issuer was contacted.
2. Compare JPMorgan's verified workbook route with Avantis's All Holdings/export
   route for the first concrete source contract, retaining fund-level eligibility
   checks. The JGRO sample provides a direct-file parser candidate; its negative
   cash, money-market holding and denominator questions remain explicit. Continue
   legitimate daily-disclosure discovery for the other candidates within their
   applicable access conditions.
3. Prefer a documented complete holdings file or feed. If the chosen source is
   embedded HTML data, specify that artifact explicitly and version the extractor;
   do not pretend an HTML capture is a CSV download or a complete portfolio.
4. Inspect two portfolio dates for the same suitable fund, then expand admission
   checks across the proposed roster. Fund names and issuer reputation do not
   establish instrument support, numerical completeness, or freshness.
5. Retain the current methodology: preserve raw precision, never normalize a
   residual, and suppress full overlap/active share when their conditions fail.

M00 remains incomplete: no approved 10–25-fund roster, fully resolved first-source
contract, or two-date accepted sample set exists. No production importer,
scheduled download, published holdings dataset, or customer source coverage has
been implemented by this assessment.
