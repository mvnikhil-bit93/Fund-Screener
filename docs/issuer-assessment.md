# Direct issuer assessment — 6 November 2026

The replacement environment can reach all six issuer discovery sites. Live
review has replaced the earlier network-only assessment: relevant terms and
policies were read, discovery routes were checked, and holdings embedded in three
official Avantis product pages were inspected. No issuer is approved for the paid
product. Rights, source completeness, and fund eligibility remain separate gates.

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
| Capital Group | [Third-party content conditions](https://www.capitalgroup.com/individual/trademarks.html) require provider permission for copying, use, or distribution of that material. This does not establish the licence for Capital Group's own holdings. | The [official fund listing](https://www.capitalgroup.com/individual/investments/returns?term=monthly) links an advisor composites route that redirects to authentication. No credentials were used. This finding does not mean every Capital Group holdings route is gated. | Establish a public complete-holdings route or authorized delivery method, then resolve first-party and third-party usage rights. |
| Avantis Investors | [Main terms](https://www.avantisinvestors.com/avantis-terms-and-conditions/en-us/) contain a limited viewing/use/download/printing licence. They do not establish permission for automated production retrieval, customer display, redistribution, or indefinite retention. | AVUS, AVUV, and AVTM product HTML contains dated structured holdings. These are not standalone CSV/XLSX downloads or proof of complete-portfolio coverage. See measured findings below. | Resolve commercial permissions, supported-position treatment, denominator/completeness, and the second-date sample before selecting an adapter. |
| Dimensional | [US terms](https://www.dimensional.com/terms-of-use-us) restrict commercial purposes without written approval and license downloaded files for personal, noncommercial use. Repeated automated access is restricted, with an exception requiring review for issuer-provided tools. | Public US discovery and terms pages are reachable. Holdings acquisition stopped after these restrictions were identified; no file quality was measured. | Establish written permission or an expressly authorized delivery tool before an automated commercial importer. |
| T. Rowe Price | [US terms](https://www.troweprice.com/en/us/terms-of-use), section 5, limit the stated grant to personal, noncommercial use and expressly restrict automated scraping and AI uses. Third-party content may require separate licensing. | An [official ETF reports page](https://www.troweprice.com/personal-investing/funds/etfs/prospectuses-reports.html) linked TCAF. Further requests stopped after the restriction was read; no fund holdings were acquired. | Resolve a written permission path before further automated holdings acquisition. |
| Fidelity | [Terms of Use](https://www.fidelity.com/terms-of-use), dated 1 July 2026, restrict commercial exploitation without written consent and third-party automated/repeated access without approval or another authorized mechanism. | The homepage presents an International Usage Agreement; no consent was accepted. The linked terms were accessible. No FELC holdings endpoint or sample was verified. | Resolve both an authorized access route and intended-use permissions before file acquisition. |
| JPMorgan Asset Management | [US individual-investor terms](https://am.jpmorgan.com/us/en/asset-management/per/terms-of-use/) require prior written consent for specified reuse or subsequent storage of protected works, subject to stated statutory exceptions. No blanket prohibition on every factual holding is concluded. | The [official ETF directory](https://am.jpmorgan.com/us/en/asset-management/per/products/fund-explorer/etf) contains a JGRO fact-sheet link. A fact sheet is not a full-holdings endpoint; no holdings file was acquired. | Establish the applicable permission or exception and then locate complete holdings. Automation permission remains unverified. |

The Capital Group [Account Agreement](https://www.capitalgroup.com/individual/account-agreement.html)
was also read. Its account-information accuracy disclaimer is not a holdings-file
licence or a measured finding that a particular portfolio file is inaccurate.
Likewise, issuer disclaimers about accuracy/completeness are not substitutes for
measuring actual files. JPMorgan's [site disclaimer](https://am.jpmorgan.com/us/en/asset-management/per/site-disclaimer/)
reinforces this distinction.

## Measured Avantis evidence

The official [US catalog](https://www.avantisinvestors.com/avantis-investments/en-us/)
verified AVUS as Avantis U.S. Equity ETF, issuer fund 114, and AVUV as Avantis
U.S. Small Cap Value ETF, issuer fund 119. Its product routes led to dated
etfHoldings arrays. AVTM was linked directly from the issuer homepage. All three
arrays have a portfolio date of **5 November 2026**. Received HTML was retained
in private review storage and inspected without executing issuer JavaScript.

| Official product page | Issuer fund number | Rows | Raw displayed-weight sum | Arithmetic gap to 100% | Rows displaying 0.00% |
| --- | --- | --- | --- | --- | --- |
| [AVUS](https://www.avantisinvestors.com/avantis-investments/en-us/avantis-us-equity-etf/) | 114 | 1,943 | 99.19% | 0.81 percentage points | 819 |
| [AVUV](https://www.avantisinvestors.com/avantis-investments/en-us/avantis-us-small-cap-value-etf/) | 119 | 793 | 99.83% | 0.17 percentage points | 91 |
| [AVTM](https://www.avantisinvestors.com/avantis-investments/en-us/avantis-total-equity-markets-etf/) | 75 | 1,709 | 98.95% | 1.05 percentage points | 815 |

These are HTML captures, not standalone holdings-file downloads. Weights are
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

## Consequences for the first importer

1. Resolve intended-use permissions before enabling recurring acquisition or
   customer display. Record the evidence for automation, retention, commercial
   analysis, display, derived outputs, redistribution, and third-party fields
   separately. No requests for permission were sent during this review.
2. Continue Capital Group's public-route investigation and Avantis's documented
   delivery discovery. These are candidates for further work, not selected
   production sources. The other four require an authorized use/access path.
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
