"""Validate the fixture transcription, not financial engine behavior.

The v1.0 document is the independent source for every golden numeric value.
Attribution remains a reference block; these checks do not run an engine.
"""

import json
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = Path(__file__).with_name("synthetic_fund.json")
SOURCE_PATH = ROOT / "docs" / "reference" / "spec-v1.0.md"
NUMBER = r"-?\d+(?:\.\d+)?"


@pytest.fixture
def fixture() -> dict[str, Any]:
    """Read exact decimal values, avoiding binary-float comparison drift."""
    data: dict[str, Any] = json.loads(
        FIXTURE_PATH.read_text(), parse_float=Decimal, parse_int=Decimal
    )
    return data


@pytest.fixture
def source() -> str:
    """Select only the original golden-fixture section."""
    document = SOURCE_PATH.read_text()
    return document.split("## 13. Golden fixture: synthetic fund\n", 1)[1].split("\n## 14.", 1)[0]


def table_rows(source: str, heading: str) -> list[dict[str, str | Decimal]]:
    """Read the specification's table values without calculating results."""
    section = source.split(f"### {heading}\n", 1)[1].split("\n### ", 1)[0]
    lines = [line for line in section.splitlines() if line.startswith("|")]
    keys = [cell.strip().lower().replace(" ", "_") for cell in lines[0].split("|")[1:-1]]
    keys = [key.replace("fund1_day_", "fund1_day") for key in keys]
    rows = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        values = [Decimal(cell) if re.fullmatch(NUMBER, cell) else cell for cell in cells]
        rows.append(dict(zip(keys, values, strict=True)))
    return rows


def labelled_numbers(text: str) -> dict[str, Decimal]:
    """Read named decimal constants from an original prose expectation."""
    return {
        label.lower().replace(" ", "_"): Decimal(value)
        for label, value in re.findall(rf"([A-Za-z][A-Za-z ]*?) ({NUMBER})", text)
    }


def test_metadata_matches_original_json_shape(fixture: dict[str, Any], source: str) -> None:
    snippet = source.split("### JSON shape\n", 1)[1].split("```json\n", 1)[1].split("\n```", 1)[0]
    shape = json.loads(snippet, parse_float=Decimal, parse_int=Decimal)
    assert set(fixture) == set(shape)
    for field in ("name", "methodology_version", "tolerances"):
        assert fixture[field] == shape[field]
    assert set(fixture["expected"]) == set(shape["expected"])


@pytest.mark.parametrize(
    ("heading", "path"),
    [
        ("Inputs", ("inputs", "securities")),
        ("Expected exposures by sector", ("expected", "exposures", "sector")),
        (
            "Expected exposures by country (cash reported separately, not as a country)",
            ("expected", "exposures", "country"),
        ),
        (
            "Expected alerts (Fund1 day 1 to day 2, threshold 0.03)",
            ("expected", "alerts"),
        ),
    ],
)
def test_table_transcription_matches_source(
    fixture: dict[str, Any], source: str, heading: str, path: tuple[str, ...]
) -> None:
    actual = fixture
    for key in path:
        actual = actual[key]
    assert actual == table_rows(source, heading)


def test_all_securities_are_unique_and_cross_referenced(fixture: dict[str, Any]) -> None:
    securities = fixture["inputs"]["securities"]
    names = [row["security"] for row in securities]
    assert names == ["A", "B", "C", "D", "E", "Cash"]
    assert len({row["figi"] for row in securities}) == len(securities)
    for block in ("crowding", "alerts"):
        assert [row["security"] for row in fixture["expected"][block]] == names


def test_overlap_constants_match_original_prose(fixture: dict[str, Any], source: str) -> None:
    fund1_bench = re.search(rf"Overlap Fund1 versus Bench: ({NUMBER})", source)
    fund1_fund2 = re.search(rf"Overlap Fund1 versus Fund2: ({NUMBER})", source)
    active_share = re.search(rf"Active share Fund1 versus Bench: ({NUMBER})", source)
    assert fund1_bench is not None
    assert fund1_fund2 is not None
    assert active_share is not None
    assert fixture["expected"]["overlap"] == {
        "fund1_vs_bench": Decimal(fund1_bench.group(1)),
        "fund1_vs_fund2": Decimal(fund1_fund2.group(1)),
        "active_share_fund1_vs_bench": {
            "one_minus_overlap": Decimal(active_share.group(1)),
            "half_sum_absolute_weight_differences": Decimal(active_share.group(1)),
        },
    }


def test_crowding_constants_match_original_prose(fixture: dict[str, Any], source: str) -> None:
    line = next(line for line in source.splitlines() if line.startswith("- Crowding"))
    expected = [
        {
            "security": security,
            "count_of_funds_holding": Decimal(count),
            "aggregate_weight": Decimal(weight),
        }
        for security, count, weight in re.findall(rf"([A-E]|Cash) (\d+), ({NUMBER})", line)
    ]
    assert len(expected) == 6
    assert fixture["expected"]["crowding"] == expected


def test_deferred_attribution_constants_are_preserved(fixture: dict[str, Any], source: str) -> None:
    section = source.split("### Expected attribution (", 1)[1].split("\n### Expected alerts", 1)[0]
    lines = [line.removeprefix("- ") for line in section.splitlines() if line.startswith("- ")]
    totals, reconciliation = lines[3].split(" Reconciliation to active return: ", 1)
    expected: dict[str, Any] = labelled_numbers(lines[0])
    expected["sectors"] = []
    for line in lines[1:3]:
        node, constants = line.split(": ", 1)
        expected["sectors"].append({"node": node, **labelled_numbers(constants)})
    expected["totals"] = labelled_numbers(totals.removeprefix("Totals: "))
    expected["reconciliation_bp"] = Decimal(reconciliation.split(" ", 1)[0])
    assert fixture["expected"]["attribution"] == expected
