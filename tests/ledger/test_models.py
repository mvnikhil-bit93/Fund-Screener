"""Acceptance cases for lossless candidate records and explicit quality states."""

from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal, localcontext
from typing import Any

import pytest
from pydantic import ValidationError

from ledger.types import Instrument, Position, Snapshot, SnapshotQuality, SourceDocument


def source_payload() -> dict[str, Any]:
    return {
        "document_id": "doc-1",
        "source_id": "issuer-1",
        "fund_id": "fund-1",
        "content_hash": "a" * 64,
        "object_path": "bronze/abc.csv",
        "fetched_at": datetime(2026, 10, 30, 22, tzinfo=UTC),
        "content_type": "text/csv",
        "adapter_version": "1.0.0",
    }


def position_payload() -> dict[str, Any]:
    return {
        "snapshot_id": "snapshot-1",
        "position_id": "row-1",
        "instrument_id": "inst-1",
        "source_ref": "doc-1#row=2",
        "source_name": "Example plc",
        "asset_category": "equity",
        "reported_weight": "0.4000",
        "original_identifiers": [{"namespace": "issuer", "value": "ABC"}],
        "quantity": "100.00",
        "market_value": "2000.00",
        "currency": "USD",
    }


def snapshot_payload() -> dict[str, Any]:
    return {
        "snapshot_id": "snapshot-1",
        "fund_id": "fund-1",
        "asof_date": date(2026, 10, 30),
        "source_document_id": "doc-1",
        "first_observed_at": datetime(2026, 10, 30, 22, tzinfo=UTC),
        "source_revision": 1,
        "parser_version": "1.0.0",
        "weight_basis": "nav",
        "total_weight": "1.0000",
        "quality": {
            "source_completeness": "complete",
            "identity_coverage": "complete",
            "classification_coverage": "complete",
            "disposition": "eligible",
        },
    }


def instrument_payload() -> dict[str, Any]:
    return {
        "instrument_id": "inst-1",
        "asset_category": "equity",
        "identity_status": "resolved",
        "origin_source_id": "issuer-1",
        "evidence_refs": ["doc-1#row=2"],
    }


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (SourceDocument, source_payload),
        (Position, position_payload),
        (Snapshot, snapshot_payload),
        (Instrument, instrument_payload),
    ],
)
def test_json_round_trip_is_lossless_and_records_are_frozen(model: Any, payload: Any) -> None:
    record = model.model_validate(payload())
    assert model.model_validate_json(record.model_dump_json()) == record
    with pytest.raises(ValidationError, match="frozen"):
        record.model_fields_set = set()
    with pytest.raises(ValidationError, match="extra"):
        model.model_validate({**payload(), "surprise": "unrecognized field"})


@pytest.mark.parametrize(
    ("model", "payload", "field"),
    [
        (SourceDocument, source_payload, "document_id"),
        (SourceDocument, source_payload, "fetched_at"),
        (Snapshot, snapshot_payload, "fund_id"),
        (Snapshot, snapshot_payload, "asof_date"),
        (Snapshot, snapshot_payload, "first_observed_at"),
        (Position, position_payload, "instrument_id"),
        (Position, position_payload, "source_ref"),
        (Position, position_payload, "reported_weight"),
        (Instrument, instrument_payload, "instrument_id"),
        (Instrument, instrument_payload, "evidence_refs"),
    ],
)
def test_required_identity_time_weight_and_provenance_fields(
    model: Any, payload: Any, field: str
) -> None:
    values = payload()
    del values[field]
    with pytest.raises(ValidationError):
        model.model_validate(values)


@pytest.mark.parametrize("value", ["", "   ", 123, None])
def test_blank_and_coerced_identifiers_are_rejected(value: Any) -> None:
    with pytest.raises(ValidationError):
        Position.model_validate({**position_payload(), "instrument_id": value})


@pytest.mark.parametrize("value", [0.4, True, 1, "NaN", "Infinity", Decimal("-Infinity")])
def test_weights_require_finite_exact_decimal_input(value: Any) -> None:
    with pytest.raises(ValidationError):
        Position.model_validate({**position_payload(), "reported_weight": value})


def test_weight_precision_and_unsupported_candidate_evidence_are_preserved() -> None:
    position = Position.model_validate(position_payload())
    assert str(position.reported_weight) == "0.4000"
    assert '"reported_weight":"0.4000"' in position.model_dump_json()
    negative = Position.model_validate({**position_payload(), "reported_weight": "-0.0300"})
    derivative = Position.model_validate({**position_payload(), "asset_category": "derivative"})
    assert str(negative.reported_weight) == "-0.0300"
    assert derivative.asset_category.value == "derivative"


def test_utc_normalization_and_naive_timestamp_rejection() -> None:
    utc = datetime(2026, 10, 30, 22, tzinfo=UTC)
    offset = utc.astimezone(timezone(timedelta(hours=5, minutes=30)))
    assert (
        SourceDocument.model_validate({**source_payload(), "fetched_at": offset}).fetched_at == utc
    )
    for value in (utc.replace(tzinfo=None), "2026-10-30T22:00:00", 1793397600):
        with pytest.raises(ValidationError):
            SourceDocument.model_validate({**source_payload(), "fetched_at": value})


def test_publication_timestamp_requires_evidence_and_cannot_follow_fetch() -> None:
    payload = source_payload()
    published = datetime(2026, 10, 30, 21, tzinfo=UTC)
    with pytest.raises(ValidationError):
        SourceDocument.model_validate({**payload, "source_published_at": published})
    record = SourceDocument.model_validate(
        {**payload, "source_published_at": published, "publication_evidence": "issuer timestamp"}
    )
    assert record.source_published_at == published
    with pytest.raises(ValidationError):
        SourceDocument.model_validate(
            {
                **payload,
                "source_published_at": published + timedelta(days=1),
                "publication_evidence": "issuer timestamp",
            }
        )


@pytest.mark.parametrize("value", [datetime(2026, 10, 30), "2026-10-30T00:00:00", 1793318400])
def test_portfolio_date_does_not_accept_timestamps(value: Any) -> None:
    with pytest.raises(ValidationError):
        Snapshot.model_validate({**snapshot_payload(), "asof_date": value})


@pytest.mark.parametrize("value", [True, 0, -1, 1.5, "1"])
def test_source_revision_is_a_positive_strict_integer(value: Any) -> None:
    with pytest.raises(ValidationError):
        Snapshot.model_validate({**snapshot_payload(), "source_revision": value})


def test_snapshot_residual_and_coverage_are_independent() -> None:
    payload = snapshot_payload()
    quality = {
        **payload["quality"],
        "classification_coverage": "partial",
        "reasons": ["unclassified", "weight_residual"],
    }
    record = Snapshot.model_validate({**payload, "total_weight": "0.9950", "quality": quality})
    assert record.quality.source_completeness.value == "complete"
    assert record.quality.disposition.value == "eligible"
    assert record.reported_residual == Decimal("0.0050")
    assert not record.has_unit_total
    assert str(record.total_weight) == "0.9950"


def test_incomplete_sources_cannot_claim_eligible_snapshot() -> None:
    payload = snapshot_payload()
    quality = {
        **payload["quality"],
        "source_completeness": "incomplete",
        "reasons": ["source_incomplete"],
    }
    with pytest.raises(ValidationError):
        Snapshot.model_validate({**payload, "quality": quality})
    quality["disposition"] = "quarantined"
    assert Snapshot.model_validate({**payload, "quality": quality}).quality.disposition.value == (
        "quarantined"
    )


@pytest.mark.parametrize(
    "reason", ["unsupported_asset", "negative_weight", "ambiguous_weight_basis"]
)
def test_known_blocking_reasons_prevent_eligible_snapshot(reason: str) -> None:
    payload = snapshot_payload()
    with pytest.raises(ValidationError):
        Snapshot.model_validate({**payload, "quality": {**payload["quality"], "reasons": [reason]}})


def test_material_residual_requires_quarantine_without_normalizing() -> None:
    payload = snapshot_payload()
    quality = {**payload["quality"], "reasons": ["weight_residual"]}
    with pytest.raises(ValidationError):
        Snapshot.model_validate({**payload, "total_weight": "0.9800", "quality": quality})
    quality["disposition"] = "quarantined"
    record = Snapshot.model_validate({**payload, "total_weight": "0.9800", "quality": quality})
    assert record.reported_residual == Decimal("0.0200")


def test_provisional_instrument_requires_source_scoped_key_and_evidence() -> None:
    payload = {**instrument_payload(), "identity_status": "provisional"}
    with pytest.raises(ValidationError):
        Instrument.model_validate(payload)
    record = Instrument.model_validate({**payload, "provisional_key": "issuer-security-code:ABC"})
    assert record.origin_source_id == "issuer-1"
    with pytest.raises(ValidationError):
        Instrument.model_validate({**payload, "provisional_key": "ABC", "evidence_refs": []})


def test_self_supersession_and_invalid_document_hash_are_rejected() -> None:
    with pytest.raises(ValidationError):
        Snapshot.model_validate({**snapshot_payload(), "supersedes_snapshot_id": "snapshot-1"})
    with pytest.raises(ValidationError):
        SourceDocument.model_validate({**source_payload(), "content_hash": "not-a-sha256"})


@pytest.mark.parametrize(
    "value",
    ["1" * 65, "1e65", "1e-65", "0." + "0" * 255 + "1", Decimal("1e1000000")],
)
def test_decimal_storage_bounds_reject_resource_exhaustion_inputs(value: Any) -> None:
    with pytest.raises(ValidationError):
        Position.model_validate({**position_payload(), "reported_weight": value})


def test_decimal_storage_bounds_preserve_supported_edges() -> None:
    for value in ("1" * 64, "1e64", "1e-64"):
        record = Position.model_validate({**position_payload(), "reported_weight": value})
        assert record.reported_weight == Decimal(value)


def test_revision_fits_arrow_signed_int64() -> None:
    assert (
        Snapshot.model_validate(
            {**snapshot_payload(), "source_revision": 2**63 - 1}
        ).source_revision
        == 2**63 - 1
    )
    with pytest.raises(ValidationError):
        Snapshot.model_validate({**snapshot_payload(), "source_revision": 2**63})


def test_revalidation_does_not_trust_constructed_or_copied_instances() -> None:
    snapshot = Snapshot.model_validate(snapshot_payload())
    invalid = snapshot.model_copy(update={"source_revision": True})
    with pytest.raises(ValidationError):
        Snapshot.model_validate(invalid)
    quality = SnapshotQuality.model_validate(snapshot_payload()["quality"])
    invalid_quality = quality.model_copy(update={"reasons": ("unrecognized_reason",)})
    with pytest.raises(ValidationError):
        Snapshot.model_validate({**snapshot_payload(), "quality": invalid_quality})


def test_residual_is_independent_of_callers_decimal_context() -> None:
    payload = snapshot_payload()
    quality = {**payload["quality"], "reasons": ["weight_residual"]}
    with localcontext() as context:
        context.prec, context.Emin, context.Emax, context.clamp = 2, -2, 2, 1
        record = Snapshot.model_validate({**payload, "total_weight": "0.9950", "quality": quality})
        assert str(record.reported_residual) == "0.0050"
        assert (context.prec, context.Emin, context.Emax, context.clamp) == (2, -2, 2, 1)


@pytest.mark.parametrize(
    "value", ["0", "1780000000", "2026-10-30T22:00:00.1234567Z", "2026-10-30T22:00:00"]
)
def test_timestamps_require_explicit_offset_and_microsecond_precision(value: str) -> None:
    with pytest.raises(ValidationError):
        SourceDocument.model_validate({**source_payload(), "fetched_at": value})


@pytest.mark.parametrize("value", ["0001-01-01T00:00:00+01:00", "9999-12-31T23:59:59-01:00"])
def test_timezone_conversion_outside_supported_dates_is_a_validation_error(value: str) -> None:
    with pytest.raises(ValidationError):
        SourceDocument.model_validate({**source_payload(), "fetched_at": value})
