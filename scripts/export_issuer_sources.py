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
        "unverified_seed_tickers",
        "access_status",
        "terms_status",
        "holdings_status",
        "sample_count",
        "production_import_enabled",
        "reviewed_at",
        "blocking_reasons",
        "research_rationale",
        "review_questions",
    ]
    writer = csv.DictWriter(output, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for issuer in sorted(register["issuers"], key=lambda item: item["research_priority"]):
        row = {
            "issuer_id": issuer["issuer_id"],
            "issuer": issuer["name"],
            "research_priority": issuer["research_priority"],
            "discovery_url": issuer["discovery_url"],
            "unverified_seed_tickers": "; ".join(issuer["seed_tickers"]),
            "access_status": issuer["access"]["status"],
            "terms_status": issuer["terms_review"]["status"],
            "holdings_status": issuer["holdings_review"]["status"],
            "sample_count": str(len(issuer["holdings_review"]["sample_ids"])),
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
