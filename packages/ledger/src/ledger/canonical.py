"""Versioned canonical record bytes; distinct from physical dataset manifests."""

import hashlib
import json
from collections.abc import Iterable

from .types import Contract, Instrument, Position, Snapshot, SourceDocument

SCHEMA_VERSION = "1.0.0"
HASH_VERSION = "fund-ledger-records-v1"
RECORDS: dict[type[Contract], tuple[str, tuple[str, ...]]] = {
    SourceDocument: ("source_document", ("document_id",)),
    Snapshot: ("snapshot", ("snapshot_id",)),
    Position: ("position", ("snapshot_id", "position_id")),
    Instrument: ("instrument", ("instrument_id",)),
}


def record_kind(record_type: type[Contract]) -> str:
    """Require an explicit known kind, including for an empty batch."""
    if record_type not in RECORDS:
        raise ValueError("unsupported record type")
    return RECORDS[record_type][0]


def validate_records[RecordT: Contract](
    record_type: type[RecordT], records: Iterable[RecordT]
) -> list[RecordT]:
    """Revalidate even constructed models, reject duplicate keys, and sort rows."""
    record_kind(record_type)
    key_fields = RECORDS[record_type][1]
    by_key: dict[tuple[str, ...], RecordT] = {}
    for record in records:
        if type(record) is not record_type:
            raise ValueError(f"expected record type {record_type.__name__}")
        validated = record_type.model_validate(record.model_dump(mode="python", warnings=False))
        key = tuple(str(getattr(validated, field)) for field in key_fields)
        if key in by_key:
            raise ValueError(f"duplicate {record_kind(record_type)} key {key!r}")
        by_key[key] = validated
    return [by_key[key] for key in sorted(by_key)]


def canonical_records[RecordT: Contract](
    record_type: type[RecordT], records: Iterable[RecordT]
) -> bytes:
    """Encode sorted rows; Decimal scale and nested sequence order are preserved."""
    validated = validate_records(record_type, records)
    envelope = {
        "hash_version": HASH_VERSION,
        "schema_version": SCHEMA_VERSION,
        "record_kind": record_kind(record_type),
        "records": [record.model_dump(mode="json") for record in validated],
    }
    return json.dumps(
        envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def hash_records[RecordT: Contract](record_type: type[RecordT], records: Iterable[RecordT]) -> str:
    """SHA-256 of the versioned canonical envelope; never consult external state."""
    return hashlib.sha256(canonical_records(record_type, records)).hexdigest()
