"""Export the issuer research register for spreadsheet review; no network or approvals."""

import argparse
import csv
import io
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "config" / "issuer_sources.json"
EXPORT = ROOT / "docs" / "issuer-sources.csv"


def render(register: dict[str, Any]) -> str:
    """Render a summary only; this is not an importer configuration validator."""
    output = io.StringIO(newline="")
    columns = [
        "issuer_id",
        "issuer",
        "research_priority",
        "discovery_url",
        "seed_tickers",
        "seed_ticker_status",
        "verified_product_tickers",
        "access_status",
        "terms_status",
        "reviewed_terms_urls",
        "automated_retrieval_rights",
        "commercial_analysis_rights",
        "customer_holdings_display_rights",
        "paid_licence_requirement",
        "official_disclosure_routes",
        "delivery_mechanisms",
        "disclosure_coverage_evidence",
        "holdings_status",
        "sample_count",
        "sample_artifact_kinds",
        "standalone_holdings_file_count",
        "portfolio_dates",
        "raw_displayed_weight_measurements",
        "sample_source_urls",
        "live_findings",
        "production_import_enabled",
        "reviewed_at",
        "blocking_reasons",
        "research_rationale",
        "review_questions",
    ]
    writer = csv.DictWriter(output, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    terms = {item["document_id"]: item for item in register["terms_documents"]}
    funds = {item["fund_id"]: item for item in register["funds"]}
    samples = {item["sample_id"]: item for item in register["samples"]}
    unknown_basis = "displayed weights; denominator unverified"
    for issuer in sorted(register["issuers"], key=lambda item: item["research_priority"]):
        reviewed_samples = [samples[key] for key in issuer["holdings_review"]["sample_ids"]]
        routes = [
            item
            for item in register["disclosure_routes"]
            if item["issuer_id"] == issuer["issuer_id"]
        ]
        row = {
            "issuer_id": issuer["issuer_id"],
            "issuer": issuer["name"],
            "research_priority": issuer["research_priority"],
            "discovery_url": issuer["discovery_url"],
            "seed_tickers": "; ".join(issuer["seed_tickers"]),
            "seed_ticker_status": issuer["seed_ticker_status"],
            "verified_product_tickers": "; ".join(
                funds[key]["ticker"] for key in issuer["holdings_review"]["fund_ids"]
            ),
            "access_status": issuer["access"]["status"],
            "terms_status": issuer["terms_review"]["status"],
            "reviewed_terms_urls": "; ".join(
                terms[key]["source_url"] for key in issuer["terms_review"]["document_ids"]
            ),
            "automated_retrieval_rights": issuer["terms_review"]["permissions"][
                "automated_retrieval"
            ],
            "commercial_analysis_rights": issuer["terms_review"]["permissions"][
                "commercial_internal_analysis"
            ],
            "customer_holdings_display_rights": issuer["terms_review"]["permissions"][
                "customer_display_of_holdings"
            ],
            "paid_licence_requirement": issuer["terms_review"]["paid_licence_requirement"],
            "official_disclosure_routes": "; ".join(item["official_url"] for item in routes),
            "delivery_mechanisms": "; ".join(item["delivery_mechanism"] for item in routes),
            "disclosure_coverage_evidence": "; ".join(item["coverage_evidence"] for item in routes),
            "holdings_status": issuer["holdings_review"]["status"],
            "sample_count": str(len(reviewed_samples)),
            "sample_artifact_kinds": "; ".join(
                sorted({item["artifact_kind"] for item in reviewed_samples})
            ),
            "standalone_holdings_file_count": str(
                sum(item["standalone_holdings_file"] for item in reviewed_samples)
            ),
            "portfolio_dates": "; ".join(
                sorted({item["portfolio_date"] for item in reviewed_samples})
            ),
            "raw_displayed_weight_measurements": "; ".join(
                f"{item['ticker']}: "
                f"{item['quality'].get('summary_weight_column', unknown_basis)}, "
                f"{item['quality']['row_count']} rows, "
                f"fraction sum {item['quality']['all_rows_reported_weight_sum_fraction']}, "
                f"{item['quality']['zero_rounded_weight_rows']} reported-zero rows; "
                "admitted W unknown"
                for item in reviewed_samples
            ),
            "sample_source_urls": "; ".join(item["source_url"] for item in reviewed_samples),
            "live_findings": issuer["live_summary"],
            "production_import_enabled": str(
                issuer["decision"]["production_import_enabled"]
            ).lower(),
            "reviewed_at": issuer["terms_review"]["reviewed_at"] or "",
            "blocking_reasons": "; ".join(issuer["decision"]["blocking_reasons"]),
            "research_rationale": issuer["research_rationale"],
            "review_questions": " | ".join(issuer["review_questions"]),
        }
        # Keep untrusted source text from becoming a spreadsheet formula.
        writer.writerow(
            {
                key: "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value
                for key, value in ((key, str(value)) for key, value in row.items())
            }
        )
    return output.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the CSV needs regeneration")
    arguments = parser.parse_args()
    rendered = render(json.loads(REGISTER.read_text(encoding="utf-8")))
    if arguments.check:
        if not EXPORT.exists() or EXPORT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Issuer CSV is stale; run python scripts/export_issuer_sources.py")
        print("Issuer CSV matches the research register.")
    else:
        EXPORT.write_text(rendered, encoding="utf-8")
        print("Exported docs/issuer-sources.csv")


if __name__ == "__main__":
    main()
