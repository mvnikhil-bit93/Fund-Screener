"""Explicit Arrow schemas and in-memory round trips; no Parquet or storage I/O."""

from collections.abc import Iterable
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

import pyarrow as pa

from .canonical import SCHEMA_VERSION, record_kind, validate_records
from .types import Contract, Instrument, Position, Snapshot, SourceDocument, decimal_text


def _text(name: str, *, nullable: bool = False) -> pa.Field:
    return pa.field(name, pa.string(), nullable=nullable)


def _decimal(name: str, *, nullable: bool = False) -> pa.Field:
    return pa.field(
        name,
        pa.string(),
        nullable=nullable,
        metadata={b"logical_type": b"exact_decimal", b"preserve_scale": b"true"},
    )


def _strings(name: str) -> pa.Field:
    return pa.field(name, pa.list_(pa.field("item", pa.string(), nullable=False)), nullable=False)


_IDENTIFIER = pa.struct([_text("namespace"), _text("value")])
_QUALITY = pa.struct(
    [
        _text("source_completeness"),
        _text("identity_coverage"),
        _text("classification_coverage"),
        _text("disposition"),
        _strings("reasons"),
    ]
)
_UTC = pa.timestamp("us", tz="UTC")
_SCHEMAS: dict[type[Contract], pa.Schema] = {
    SourceDocument: pa.schema(
        [
            _text("document_id"),
            _text("source_id"),
            _text("fund_id"),
            _text("content_hash"),
            _text("object_path"),
            pa.field("fetched_at", _UTC, nullable=False),
            _text("content_type"),
            _text("adapter_version"),
            pa.field("source_published_at", _UTC),
            _text("publication_evidence", nullable=True),
        ]
    ),
    Snapshot: pa.schema(
        [
            _text("snapshot_id"),
            _text("fund_id"),
            pa.field("asof_date", pa.date32(), nullable=False),
            _text("source_document_id"),
            pa.field("first_observed_at", _UTC, nullable=False),
            pa.field("source_revision", pa.int64(), nullable=False),
            _text("parser_version"),
            _text("weight_basis"),
            _decimal("total_weight"),
            pa.field("quality", _QUALITY, nullable=False),
            _text("supersedes_snapshot_id", nullable=True),
        ]
    ),
    Position: pa.schema(
        [
            _text("snapshot_id"),
            _text("position_id"),
            _text("instrument_id"),
            _text("source_ref"),
            _text("source_name"),
            _text("asset_category"),
            _decimal("reported_weight"),
            pa.field(
                "original_identifiers",
                pa.list_(pa.field("item", _IDENTIFIER, nullable=False)),
                nullable=False,
            ),
            _decimal("quantity", nullable=True),
            _decimal("market_value", nullable=True),
            _text("currency", nullable=True),
            _decimal("calculated_nav_weight", nullable=True),
        ]
    ),
    Instrument: pa.schema(
        [
            _text("instrument_id"),
            _text("asset_category"),
            _text("identity_status"),
            _text("origin_source_id"),
            _strings("evidence_refs"),
            _text("provisional_key", nullable=True),
        ]
    ),
}


def schema_for(record_type: type[Contract]) -> pa.Schema:
    """Return the exact physical schema, including kind and schema-version metadata."""
    kind = record_kind(record_type)
    return _SCHEMAS[record_type].with_metadata(
        {
            b"record_kind": kind.encode("ascii"),
            b"schema_version": SCHEMA_VERSION.encode("ascii"),
        }
    )


def _encode(value: Any) -> Any:
    if isinstance(value, Decimal):
        return decimal_text(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _encode(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_encode(item) for item in value]
    return value


def _decode(value: Any) -> Any:
    # Arrow list containers are restored to the immutable model's tuple contract.
    if isinstance(value, list):
        return tuple(_decode(item) for item in value)
    if isinstance(value, dict):
        return {key: _decode(item) for key, item in value.items()}
    if isinstance(value, (date, datetime)):
        return value
    return value


def to_arrow[RecordT: Contract](record_type: type[RecordT], records: Iterable[RecordT]) -> pa.Table:
    """Validate a homogeneous batch before serializing exact financial values."""
    validated = validate_records(record_type, records)
    rows = [_encode(record.model_dump(mode="python")) for record in validated]
    return pa.Table.from_pylist(rows, schema=schema_for(record_type))


def from_arrow[RecordT: Contract](record_type: type[RecordT], table: pa.Table) -> list[RecordT]:
    """Reject mismatched physical contracts; do not silently cast or drop fields."""
    if not table.schema.equals(schema_for(record_type), check_metadata=True):
        raise ValueError("Arrow schema does not match the requested record contract")
    records = [record_type.model_validate(_decode(row)) for row in table.to_pylist()]
    return validate_records(record_type, records)
