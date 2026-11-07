"""Money-market fund positions keep security identity and source precision."""

import json
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ledger.arrow import from_arrow, to_arrow
from ledger.canonical import canonical_records, hash_records
from ledger.types import AssetCategory, Instrument, Position


def money_market_position() -> Position:
    return Position.model_validate(
        {
            "snapshot_id": "snapshot-1",
            "position_id": "row-1",
            "instrument_id": "money-fund-a-institutional",
            "source_ref": "doc-1#row=8",
            "source_name": "Synthetic Money Fund A Institutional",
            "asset_category": "money_market_fund",
            "reported_weight": "0.016200",
            "original_identifiers": [{"namespace": "issuer", "value": "fund-a-inst"}],
            "quantity": "100.1250",
            "market_value": "100.1300",
            "currency": "USD",
        }
    )


def test_share_classes_and_cash_keep_distinct_identities_through_serialization() -> None:
    first = money_market_position()
    second = Position.model_validate(
        {
            **first.model_dump(),
            "position_id": "row-2",
            "instrument_id": "money-fund-a-retail",
            "source_ref": "doc-1#row=9",
            "source_name": "Synthetic Money Fund A Retail",
            "original_identifiers": [{"namespace": "issuer", "value": "fund-a-retail"}],
        }
    )
    cash = Position.model_validate(
        {
            **first.model_dump(),
            "position_id": "row-3",
            "instrument_id": "cash-usd",
            "source_ref": "doc-1#row=10",
            "source_name": "USD cash",
            "asset_category": "cash",
            "original_identifiers": [],
        }
    )
    positions = [first, second, cash]
    instruments = [
        Instrument.model_validate(
            {
                "instrument_id": row.instrument_id,
                "asset_category": row.asset_category,
                "identity_status": "resolved",
                "origin_source_id": "issuer-a",
                "evidence_refs": [row.source_ref],
            }
        )
        for row in positions
    ]

    for model, records in ((Position, positions), (Instrument, instruments)):
        expected = sorted(records, key=lambda row: getattr(row, "position_id", row.instrument_id))
        restored = from_arrow(model, to_arrow(model, list(reversed(records))))
        assert restored == expected
        assert [model.model_validate_json(row.model_dump_json()) for row in restored] == expected
        assert canonical_records(model, restored) == canonical_records(model, records)
        canonical = json.loads(canonical_records(model, restored))["records"]
        assert {row["instrument_id"] for row in canonical} == {
            "money-fund-a-institutional",
            "money-fund-a-retail",
            "cash-usd",
        }
        assert sum(row["asset_category"] == "money_market_fund" for row in canonical) == 2
        assert sum(row["asset_category"] == "cash" for row in canonical) == 1


def test_relabeling_a_money_market_fund_as_cash_changes_canonical_identity() -> None:
    original = money_market_position()
    relabeled = Position.model_validate({**original.model_dump(), "asset_category": "cash"})
    assert original.asset_category == AssetCategory.MONEY_MARKET_FUND
    assert original.asset_category != AssetCategory.CASH
    assert hash_records(Position, [original]) != hash_records(Position, [relabeled])


def test_money_market_candidate_retains_signed_values_without_par_assumptions() -> None:
    original = money_market_position()
    candidate = Position.model_validate(
        {
            **original.model_dump(),
            "reported_weight": "-0.0000100",
            "quantity": "-100.1250",
            "market_value": "-100.1300",
        }
    )
    restored = from_arrow(Position, to_arrow(Position, [candidate]))[0]
    assert restored.asset_category == AssetCategory.MONEY_MARKET_FUND
    assert str(restored.reported_weight) == "-0.0000100"
    assert str(restored.quantity) == "-100.1250"
    assert str(restored.market_value) == "-100.1300"
    assert restored.market_value != restored.quantity
    assert restored.reported_weight == Decimal("-0.0000100")


def test_money_market_identity_still_requires_evidence_and_a_provisional_key() -> None:
    payload = {
        "instrument_id": "issuer-a:unresolved-money-fund",
        "asset_category": "money_market_fund",
        "identity_status": "provisional",
        "origin_source_id": "issuer-a",
        "evidence_refs": ["doc-1#row=8"],
        "provisional_key": "issuer-a:source-security-code:123",
    }
    record = Instrument.model_validate(payload)
    assert record.asset_category == AssetCategory.MONEY_MARKET_FUND
    assert record.identity_status.value == "provisional"
    with pytest.raises(ValidationError, match="evidence_refs"):
        Instrument.model_validate({**payload, "evidence_refs": []})
    with pytest.raises(ValidationError, match="provisional identity"):
        Instrument.model_validate({**payload, "provisional_key": None})
