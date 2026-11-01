"""M02 acceptance: canonical identity and lossless, schema-checked Arrow batches."""

import json
from decimal import Decimal, localcontext

import pyarrow as pa
import pytest
from hypothesis import given
from hypothesis import strategies as st

from ledger.arrow import from_arrow, schema_for, to_arrow
from ledger.canonical import canonical_records, hash_records
from ledger.types import Instrument, Position, Snapshot, SourceDocument


def document(document_id: str = "doc-1", instant: str = "2026-10-30T17:00:00Z"):
    return SourceDocument.model_validate_json(
        json.dumps(
            {
                "document_id": document_id,
                "source_id": "issuer-a",
                "fund_id": "fund-a",
                "content_hash": "a" * 64,
                "object_path": "bronze/a.csv",
                "fetched_at": instant,
                "content_type": "text/csv",
                "adapter_version": "1.0.0",
            }
        )
    )


def position(position_id: str = "row-1", weight: str = "0.4000"):
    return Position.model_validate_json(
        json.dumps(
            {
                "snapshot_id": "snapshot-1",
                "position_id": position_id,
                "instrument_id": "instrument-a",
                "source_ref": "row:2",
                "source_name": "Example",
                "asset_category": "equity",
                "reported_weight": weight,
                "original_identifiers": [{"namespace": "issuer", "value": "source-a"}],
                "quantity": "120.00",
                "market_value": "4000.000",
                "currency": "USD",
            }
        )
    )


def snapshot():
    return Snapshot.model_validate_json(
        json.dumps(
            {
                "snapshot_id": "snapshot-1",
                "fund_id": "fund-a",
                "asof_date": "2026-10-30",
                "source_document_id": "doc-1",
                "first_observed_at": "2026-10-30T17:00:00Z",
                "source_revision": 1,
                "parser_version": "1.0.0",
                "weight_basis": "nav",
                "total_weight": "0.9950",
                "quality": {
                    "source_completeness": "complete",
                    "identity_coverage": "partial",
                    "classification_coverage": "unknown",
                    "disposition": "eligible",
                    "reasons": ["unresolved_identity", "unclassified", "weight_residual"],
                },
            }
        )
    )


def instrument():
    return Instrument.model_validate_json(
        json.dumps(
            {
                "instrument_id": "instrument-a",
                "asset_category": "equity",
                "identity_status": "resolved",
                "origin_source_id": "issuer-a",
                "evidence_refs": ["doc-1:row-2"],
            }
        )
    )


@pytest.mark.parametrize("factory", [document, position, snapshot, instrument])
def test_arrow_roundtrip_preserves_every_field_and_declared_schema(factory):
    record = factory()
    record_type = type(record)
    table = to_arrow(record_type, [record])
    assert set(table.schema.names) == set(record_type.model_fields)
    assert table.schema.equals(schema_for(record_type), check_metadata=True)
    assert from_arrow(record_type, table) == [record]
    assert canonical_records(record_type, from_arrow(record_type, table)) == (
        canonical_records(record_type, [record])
    )


@pytest.mark.parametrize(
    ("factory", "updates"),
    [
        (
            document,
            {
                "source_published_at": "2026-10-30T16:00:00Z",
                "publication_evidence": "issuer publication timestamp",
            },
        ),
        (position, {"calculated_nav_weight": "0.40001"}),
        (snapshot, {"source_revision": 2, "supersedes_snapshot_id": "snapshot-older"}),
        (instrument, {"identity_status": "provisional", "provisional_key": "issuer-code:A"}),
    ],
)
def test_optional_evidence_revision_and_provisional_fields_roundtrip(factory, updates):
    original = factory()
    record = type(original).model_validate({**original.model_dump(), **updates})
    assert from_arrow(type(record), to_arrow(type(record), [record])) == [record]


def test_decimal_precision_and_temporal_arrow_types_are_explicit():
    assert schema_for(Position).field("reported_weight").type == pa.string()
    assert schema_for(Snapshot).field("asof_date").type == pa.date32()
    assert schema_for(SourceDocument).field("fetched_at").type == pa.timestamp("us", tz="UTC")
    restored = from_arrow(Position, to_arrow(Position, [position()]))[0]
    assert str(restored.reported_weight) == "0.4000"
    assert str(restored.quantity) == "120.00"
    assert str(restored.market_value) == "4000.000"


@given(st.permutations([0, 1, 2, 3]))
def test_record_order_does_not_change_canonical_bytes(order):
    records = [document(f"doc-{i}") for i in range(4)]
    assert canonical_records(SourceDocument, [records[i] for i in order]) == (
        canonical_records(SourceDocument, records)
    )


def test_hash_includes_values_precision_and_record_kind():
    assert hash_records(Position, [position(weight="0.4")]) != (
        hash_records(Position, [position(weight="0.4000")])
    )
    assert hash_records(Position, [position(weight="0.4")]) != (
        hash_records(Position, [position(weight="0.5")])
    )
    assert hash_records(Position, []) != hash_records(SourceDocument, [])
    envelope = json.loads(canonical_records(Position, [position()]))
    assert envelope["schema_version"] == "1.0.0"
    assert envelope["hash_version"] == "fund-ledger-records-v1"
    assert envelope["record_kind"] == "position"


def test_canonical_format_has_a_fixed_interoperability_vector():
    expected = (
        b'{"hash_version":"fund-ledger-records-v1","record_kind":"position",'
        b'"records":[],"schema_version":"1.0.0"}'
    )
    assert canonical_records(Position, []) == expected
    assert hash_records(Position, []) == (
        "147b8ea762c07c34d92aa576f62b6e5faa8e1a7414c23fe4e11a2761c77c1a37"
    )


def test_equivalent_instants_and_dictionary_order_hash_identically():
    assert hash_records(SourceDocument, [document()]) == hash_records(
        SourceDocument, [document(instant="2026-10-30T18:00:00+01:00")]
    )
    data = document().model_dump(mode="json")
    reordered = dict(reversed(list(data.items())))
    record = SourceDocument.model_validate_json(json.dumps(reordered))
    assert hash_records(SourceDocument, [record]) == hash_records(SourceDocument, [document()])


@pytest.mark.parametrize("operation", [canonical_records, to_arrow])
def test_duplicate_keys_and_mixed_record_types_are_rejected(operation):
    with pytest.raises(ValueError, match="duplicate"):
        operation(Position, [position(), position()])
    with pytest.raises(ValueError, match="record type"):
        operation(Position, [document()])


def test_position_primary_key_includes_snapshot():
    first = position()
    second = Position.model_validate(
        {
            **first.model_dump(),
            "snapshot_id": "snapshot-2",
        }
    )
    assert len(from_arrow(Position, to_arrow(Position, [first, second]))) == 2


@pytest.mark.parametrize("record_type", [SourceDocument, Snapshot, Position, Instrument])
def test_empty_arrow_batches_keep_their_type(record_type):
    table = to_arrow(record_type, [])
    assert table.schema.equals(schema_for(record_type), check_metadata=True)
    assert from_arrow(record_type, table) == []


def test_reader_rejects_wrong_schema_missing_metadata_and_required_nulls():
    table = to_arrow(Position, [position()])
    with pytest.raises(ValueError, match="schema"):
        from_arrow(Position, table.append_column("unexpected", pa.array(["value"])))
    with pytest.raises(ValueError, match="schema"):
        from_arrow(Position, table.replace_schema_metadata(None))
    rows = table.to_pylist()
    rows[0]["instrument_id"] = None
    invalid = pa.Table.from_pylist(rows, schema=schema_for(Position))
    with pytest.raises(ValueError):
        from_arrow(Position, invalid)


@given(st.integers(min_value=-100000, max_value=100000), st.integers(min_value=0, max_value=8))
def test_decimal_roundtrip_preserves_scale_and_value(coefficient, scale):
    value = Decimal(coefficient).scaleb(-scale)
    record = position(weight=str(value))
    restored = from_arrow(Position, to_arrow(Position, [record]))[0]
    assert restored.reported_weight.as_tuple() == record.reported_weight.as_tuple()


def test_hashing_revalidates_unsafe_constructed_records():
    invalid = Position.model_construct(
        **{**position().model_dump(), "reported_weight": float("nan")}
    )
    with pytest.raises(ValueError):
        canonical_records(Position, [invalid])


def test_decimal_serialization_is_independent_of_callers_capitals_setting():
    record = position(weight="1E-10")
    with localcontext() as context:
        context.capitals = 0
        lower_json = record.model_dump_json()
        lower_bytes = canonical_records(Position, [record])
        lower_arrow = to_arrow(Position, [record]).to_pylist()
        context.capitals = 1
        assert record.model_dump_json() == lower_json
        assert canonical_records(Position, [record]) == lower_bytes
        assert to_arrow(Position, [record]).to_pylist() == lower_arrow
