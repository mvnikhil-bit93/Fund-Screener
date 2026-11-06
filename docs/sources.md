# Source feasibility register — M00

Latest assessment: 6 November 2026 (UTC).

Status: **official daily-disclosure routes verified for Avantis and JPMorgan;
no source admitted for production.** Direct issuer sourcing remains viable. The
reviewed evidence does not establish that underlying factual holdings require a
paid data licence. Website access conditions, factual reuse, proprietary additions,
original-document retention and financial suitability are separate questions.

## Current evidence and mapping

- [Six-issuer assessment](issuer-assessment.md): source-linked findings and measurements.
- [Canonical issuer mapping](../config/issuer_sources.json): routes, evidence,
  terms applicability, field categories, scoped decisions, samples and admission.
- [Spreadsheet summary](issuer-sources.csv): generated from the JSON mapping.
- [Register guide](source-register.md): how to add evidence and extend the mapping.
- [Importer plan](importer-plan.md): source contract, then M04 acquisition and
  M05 parsing; no production importer is implemented by this research change.
- [JPMorgan validation](jpmorgan-source-validation.md): complete 31-fund active
  equity screen, second-date check, weight diagnostics and an unapproved scope proposal.

| Issuer | Verified finding | Next evidence needed |
| --- | --- | --- |
| Capital Group | Public listing uses dynamic product discovery; the previously tested advisor composites route requires authentication. Third-party notices do not establish rights in all first-party holdings facts. | Official daily disclosure route, actual fields and specific conditions |
| Avantis | Product-specific notice describes each position's disclosure before trading each business day. AVUS All Holdings page and client-side CSV export mechanism verified. | Second date, denominator, supported positions and specific access/use basis |
| Dimensional | General website commercial restrictions and an automation clause concerning damaging/overburdening conduct, with an issuer-tool exception | Official disclosure/tool and applicable conditions; no holdings sample acquired |
| T. Rowe Price | Explicit scraping restriction, section-specific terms precedence and a separate approved/issuer-tool clause must be read together | A supported disclosure mechanism; no exception assumed or holdings acquired |
| Fidelity | Website commercial/automated-access clauses recognize authorized tools and page-specific terms; homepage international-use gate unaccepted | Legitimate official disclosure route and conditions; no holdings sample acquired |
| JPMorgan | All 31 active equity funds screened: 13 derivative/short exclusions; all 31 hold money-market investments. JGRO's repeat download still reports 5 November; financial rows unchanged. | Explicit scope decision, second date, denominator/calendar, identities, ten-fund roster and operation-specific use basis; no source admitted |

The mapping preserves earlier general-site decisions as history and links scoped
superseding reviews. Missing permission text does not prove permission is needed
or paid licensing is mandatory. Actual applicable restrictions and unresolved
material rights still govern production admission under the specification.

## Measured holdings evidence

Five initial samples cover four funds on **5 November 2026**: three Avantis
product-page captures, an additional AVUS All Holdings page, and one JGRO XLSX.
The two AVUS captures contain identical holdings; they are not two portfolio dates.
The later JGRO repeat acquisition changes document metadata only and is recorded
separately. Screening 31 product JSON datasets does not mean 31 XLSX files or
31 admitted funds; their aggregate findings are in the linked validation mapping.

| Fund | Positions | Reported weight totals | Reported zero-weight rows |
| --- | ---: | --- | ---: |
| AVUS | 1,943 | 99.19%; exact denominator unverified | 819 |
| AVUV | 793 | 99.83%; exact denominator unverified | 91 |
| AVTM | 1,709 | 98.95%; exact denominator unverified | 815 |
| JGRO | 140 | Market Value 100.00%; Net Assets 100.06% | 2 in each column |

These Decimal totals include all source rows and are not admitted analytical W.
Avantis's client CSV exporter passes through the same rounded weights. Its separate
Daily Pricing Basket is different data and cannot be used to repair the portfolio.
The CSV mechanism was verified by static code inspection; no browser-generated
CSV file was captured. JPMorgan provides a real standalone XLSX download.

All samples need instrument and numerical review. In JGRO, negative USD cash
value/quantity displays as zero after weight rounding; a money-market holding
also requires treatment. The market-value column summing to 100% does not prove
eligibility or justify silently preferring it over net assets. Avantis samples
include sweep vehicles, rights and other unsupported or unresolved types.

Every source row remains represented in the assessment. No weights were normalized,
no balancing cash was added, and no financial methodology changed. Sector/industry
labels and country meanings remain separate from factual quantities/weights and
are not adopted automatically as the product's taxonomy. Original source files,
scripts and constituent rows remain outside Git.

## Network and remaining discovery

The six issuer discovery hosts plus api.github.com are active. Avantis and JPMorgan
route investigation used those approved hosts, with normal proxy/TLS and no gate
bypass. Capital Group's public product discovery depends on an observed Coveo host
outside the active policy; its details are recorded, but no request or token use
was attempted. A failed advisor route does not imply all holdings are gated.

The saved environment draft preserves current settings and setup/start instructions.
It includes the previously proposed avantisinvestors.prospectus-express.com for
observed quarterly-report links, plus www.ecfr.gov to verify current Rule 6c-11 text.
Revision 5 also adds connect.rightprospectus.com after the official JGRO prospectus
wrapper linked it. All three remain outside active policy. Saving the draft does not enable them or publish
the environment. No regulatory text, quarterly-report content or fund-specific
reliance on the rule is claimed live verified. Quarterly reports would not by
themselves demonstrate daily delivery history.

## Completion criteria and next adapter decision

M00 still needs a suitable launch roster, a complete first-source contract,
scoped access/use findings, calendar/deadline, denominator and identity evidence,
and two accepted portfolio dates for the same suitable fund. A paid feed is not
assumed to be the solution to these gaps.

Compare JPMorgan's workbook route with Avantis's All Holdings route. JPMorgan now
provides a concrete file-format candidate, while both samples expose material
position/precision questions. Do not choose an analytical denominator to force
unit totals or silently treat money-market/sweep investments as explicit cash.
Any change to supported positions or numerical rules is a separate reviewed
methodology decision. No ten-fund roster, scheduled importer or customer coverage
is claimed complete.

The latest JPMorgan screen establishes zero admissions under current scope.
The narrow proposal to support identified money-market fund units separately
from cash would leave five structural research candidates: JAVA, JPEF, LGDS,
LVDS and JPSV. It remains unapproved and would not by itself establish ten funds
or remove numerical/identity/source-use gaps. The full proposal and alternatives
are in the JPMorgan validation report; the active specification is unchanged.

## Earlier investigation

The initial environment blocked issuer requests before any website response.
The replacement published environment enabled all six discovery hosts on
6 November. The first live review recorded general terms and three Avantis
product-page samples. This refinement corrects overbroad licensing inferences
and adds actual disclosure/delivery evidence. Historical observations remain in
the mapping and decisions log; they do not describe current access or approvals.
