# Source feasibility register — M00

Latest assessment: 6 November 2026 (UTC).

Status: **partial live review completed; no source admitted for production.**
Official issuer downloads remain the preferred acquisition route. The replacement
environment now permits the six issuer discovery sites, and live responses have
been verified. The earlier environment-network block is resolved for those hosts.

## Current evidence and mapping

- [Six-issuer assessment](issuer-assessment.md): source-linked rights/access
  findings and actual sample measurements.
- [Canonical issuer mapping](../config/issuer_sources.json): separate access,
  terms, scoped permissions, funds, samples, field mappings, and admission states.
- [Spreadsheet summary](issuer-sources.csv): generated from the JSON mapping.
- [Register guide](source-register.md): how to add evidence and extend the mapping.
- [Importer plan](importer-plan.md): M00 gates followed by bounded M04 acquisition
  and M05 parsing; no importer is implemented by this research change.

| Issuer | Findings so far | Main outstanding requirement |
| --- | --- | --- |
| Capital Group | Public US policy pages reviewed; linked advisor composites route led to authentication | Establish public complete holdings or authorized access and applicable first-party rights; observed third-party restrictions do not describe every issuer-owned holding |
| Avantis | Limited download licence; three dated HTML-embedded holdings arrays inspected, including AVUS and AVUV | Resolve commercial/automation scope, obtain full files and a second portfolio date, and review unsupported positions/denominator/completeness |
| Dimensional | US terms restrict commercial use without written approval and repeated automated access | Establish an authorized delivery and use basis before holdings acquisition |
| T. Rowe Price | US terms restrict commercial use and explicitly address automated scraping/AI use | Obtain an appropriate permission path; no further acquisition after that finding |
| Fidelity | Personal/noncommercial and automated-access restrictions; international-use agreement at homepage | Resolve permissions and authorized access; no agreement accepted or holdings fetched |
| JPMorgan Asset Management | US terms restrict reuse/storage of protected works without consent, subject to stated statutory exceptions | Establish applicable permission basis; a verified directory/factsheet link is not a full-holdings endpoint |

These are evidence-based research findings, not legal approval or a declaration
that every underlying fact is protected by the same rights. Applicable fund/file
terms, third-party material, intended use, and exceptions need scoped review.

## Measured holdings evidence

Three official Avantis product pages contain holdings arrays dated **5 November
2026**. They are HTML-embedded source data, not standalone CSV/XLSX downloads.

| Fund | Rows | Raw displayed-weight total | Rows displaying 0.00% |
| --- | ---: | ---: | ---: |
| AVUS | 1,943 | 99.19% | 819 |
| AVUV | 793 | 99.83% | 91 |
| AVTM | 1,709 | 98.95% | 815 |

Totals use the issuer's displayed percentage strings with Decimal arithmetic.
They are not admitted analytical W: completeness, denominator, and eligibility
are unresolved, and the samples include unsupported or unresolved position types.
A rounded zero is not evidence of a genuinely zero holding. No weights were
normalized, no balancing cash was added, and no financial methodology changed.
See the assessment and mapping for scope distinctions and evidence hashes.

All three observations share one portfolio date. No two-date history, clean
10-fund roster, daily standalone delivery, or complete first-source contract is
established. The original pages and extracted constituent rows remain in private
ignored review cache; only limited findings and metadata are committed.

## Network and remaining access

The six discovery hosts plus api.github.com are active in the replacement
runtime. Earlier blocked-policy observations remain historical evidence in the
mapping and decisions log; they do not describe current issuer-site access.

The official Avantis catalog links quarterly holdings documents on
avantisinvestors.prospectus-express.com. That exact host is now proposed in the
saved draft, preserving published settings and restored setup/start instructions;
it has not been requested while absent from the active policy. Review/save and
publish the draft to enable investigation of those documents. Quarterly reports
must not be relabeled as daily history. Their applicable terms and any further
redirect destinations still require inspection.

The linked res.avantisinvestors.com host serves factsheet leads. It was not
requested or added to the network draft; a factsheet does not establish complete
holdings. No wildcard, alternate proxy, account, consent acceptance, or access-gate
bypass was used. Discovery URLs and permission requirements are kept separate.

## Completion criteria

M00 remains open until the first-source contract includes a verified launch
roster, authoritative complete-holdings endpoints, applicable rights evidence,
calendar/deadline, units/denominator, measured metric eligibility, and two
permitted files from distinct portfolio dates. Unresolved commercial rights
remain explicit pilot blockers even when limited research is permitted.

The current plan is to resolve these source-specific issues before selecting an
adapter. Changing the supported treatment of sweep funds, rights, warrants, or
other incidental positions requires a reviewed scope/methodology decision;
rounded 0.00% does not justify silently deleting them.

## Earlier investigation

On 1 November, ordinary sandbox requests could not connect to the proxy and
narrow escalation was rejected because the issuer destinations were outside the
then-enforced policy. This was an environment limitation, not an issuer response.
The original Capital Group/Avantis draft entries were later expanded to the six
research candidates. On 6 November, the replacement published environment applied
those entries and enabled the live assessment above. No earlier failed request
is treated as evidence that a source is unavailable or licensed.
