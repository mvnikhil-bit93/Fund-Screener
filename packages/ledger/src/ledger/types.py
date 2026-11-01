"""Immutable candidate-record contracts (schema 1.0.0); no ingestion or I/O.

Candidates preserve unsupported rows for diagnosis. Publication and cross-row
reconciliation remain separate checks; declaring metadata is not verification.
"""

import re
from datetime import UTC, date, datetime
from decimal import Context, Decimal, InvalidOperation, localcontext
from enum import StrEnum
from typing import Annotated, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    StrictInt,
    StringConstraints,
    model_validator,
)


def _decimal(value: object) -> Decimal:
    if not isinstance(value, (Decimal, str)):
        raise ValueError("use a Decimal or decimal string, never a float or integer")
    if isinstance(value, str) and len(value) > 256:
        raise ValueError("decimal input exceeds the 256-character storage bound")
    try:
        parsed = Decimal(value)
    except InvalidOperation as error:
        raise ValueError("invalid decimal string") from error
    if not parsed.is_finite():
        raise ValueError("financial values must be finite")
    _, digits, exponent = parsed.as_tuple()
    if len(digits) > 64 or not isinstance(exponent, int) or abs(exponent) > 64:
        raise ValueError("decimals require at most 64 coefficient digits and exponent -64..64")
    return parsed


def decimal_text(value: Decimal) -> str:
    """Preserve decimal precision with exponent casing independent of context."""
    return str(value).upper()


def _timestamp_input(value: object) -> object:
    if not isinstance(value, (datetime, str)):
        raise ValueError("timestamp must be an aware datetime or ISO timestamp")
    if isinstance(value, str) and not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})",
        value,
    ):
        raise ValueError("ISO timestamps require an explicit offset and microsecond precision")
    return value


def _utc(value: datetime) -> datetime:
    if value.utcoffset() is None:
        raise ValueError("knowledge timestamps require an explicit UTC offset")
    try:
        return value.astimezone(UTC)
    except OverflowError as error:
        raise ValueError("timestamp is outside the supported UTC date range") from error


def _portfolio_date(value: object) -> object:
    if type(value) is date or (
        isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)
    ):
        return value
    raise ValueError("portfolio dates require date or YYYY-MM-DD, not a timestamp")


NonEmpty = Annotated[str, StringConstraints(strict=True, min_length=1, pattern=r"\S")]
Sha256 = Annotated[str, StringConstraints(strict=True, pattern=r"^[0-9a-f]{64}$")]
Currency = Annotated[str, StringConstraints(strict=True, pattern=r"^[A-Z]{3}$")]
ExactDecimal = Annotated[
    Decimal,
    BeforeValidator(_decimal),
    PlainSerializer(decimal_text, return_type=str, when_used="json"),
]
UtcDatetime = Annotated[datetime, BeforeValidator(_timestamp_input), AfterValidator(_utc)]
PortfolioDate = Annotated[date, BeforeValidator(_portfolio_date)]


class Contract(BaseModel):
    """Frozen records reject unknown fields rather than silently discarding them."""

    model_config = ConfigDict(
        extra="forbid", frozen=True, validate_default=True, revalidate_instances="always"
    )


class AssetCategory(StrEnum):
    EQUITY = "equity"
    ADR = "adr"
    CASH = "cash"
    DERIVATIVE = "derivative"
    OTHER = "other"


class IdentityStatus(StrEnum):
    RESOLVED = "resolved"
    PROVISIONAL = "provisional"


class Completeness(StrEnum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    UNKNOWN = "unknown"


class Coverage(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class Disposition(StrEnum):
    ELIGIBLE = "eligible"
    QUARANTINED = "quarantined"
    UNSUPPORTED = "unsupported"


class WeightBasis(StrEnum):
    NAV = "nav"
    REPORTED_ASSETS = "reported_assets"
    UNKNOWN = "unknown"


class QualityReason(StrEnum):
    SOURCE_INCOMPLETE = "source_incomplete"
    UNRESOLVED_IDENTITY = "unresolved_identity"
    UNCLASSIFIED = "unclassified"
    WEIGHT_RESIDUAL = "weight_residual"
    UNSUPPORTED_ASSET = "unsupported_asset"
    NEGATIVE_WEIGHT = "negative_weight"
    AMBIGUOUS_WEIGHT_BASIS = "ambiguous_weight_basis"
    UNSUPPORTED_CURRENCY = "unsupported_currency"


class SnapshotQuality(Contract):
    source_completeness: Completeness
    identity_coverage: Coverage
    classification_coverage: Coverage
    disposition: Disposition
    reasons: tuple[QualityReason, ...] = ()

    @model_validator(mode="after")
    def consistent_states(self) -> Self:
        reasons = set(self.reasons)
        if len(reasons) != len(self.reasons):
            raise ValueError("quality reasons must be unique")
        for incomplete, reason in (
            (self.source_completeness != Completeness.COMPLETE, QualityReason.SOURCE_INCOMPLETE),
            (self.identity_coverage != Coverage.COMPLETE, QualityReason.UNRESOLVED_IDENTITY),
            (self.classification_coverage != Coverage.COMPLETE, QualityReason.UNCLASSIFIED),
        ):
            if incomplete != (reason in reasons):
                raise ValueError(f"coverage and {reason} reason must agree")
        blockers = {
            QualityReason.SOURCE_INCOMPLETE,
            QualityReason.UNSUPPORTED_ASSET,
            QualityReason.NEGATIVE_WEIGHT,
            QualityReason.AMBIGUOUS_WEIGHT_BASIS,
            QualityReason.UNSUPPORTED_CURRENCY,
        }
        if self.disposition == Disposition.ELIGIBLE and reasons & blockers:
            raise ValueError("known blocking quality reasons prohibit eligible disposition")
        if self.disposition != Disposition.ELIGIBLE and not reasons:
            raise ValueError("an ineligible disposition requires explicit reasons")
        return self


class SourceDocument(Contract):
    document_id: NonEmpty
    source_id: NonEmpty
    fund_id: NonEmpty
    content_hash: Sha256
    object_path: NonEmpty
    fetched_at: UtcDatetime
    content_type: NonEmpty
    adapter_version: NonEmpty
    source_published_at: UtcDatetime | None = None
    publication_evidence: NonEmpty | None = None

    @model_validator(mode="after")
    def evidenced_publication(self) -> Self:
        if self.source_published_at is not None:
            if self.publication_evidence is None:
                raise ValueError("source publication time requires evidence")
            if self.source_published_at > self.fetched_at:
                raise ValueError("source publication cannot follow observation")
        elif self.publication_evidence is not None:
            raise ValueError("publication evidence requires a source publication timestamp")
        return self


class ExternalIdentifier(Contract):
    namespace: NonEmpty
    value: NonEmpty


class Position(Contract):
    """One source row, including unsupported candidates retained for diagnosis."""

    snapshot_id: NonEmpty
    position_id: NonEmpty
    instrument_id: NonEmpty
    source_ref: NonEmpty
    source_name: NonEmpty
    asset_category: AssetCategory
    reported_weight: ExactDecimal
    original_identifiers: tuple[ExternalIdentifier, ...] = ()
    quantity: ExactDecimal | None = None
    market_value: ExactDecimal | None = None
    currency: Currency | None = None
    calculated_nav_weight: ExactDecimal | None = None


class Instrument(Contract):
    instrument_id: NonEmpty
    asset_category: AssetCategory
    identity_status: IdentityStatus
    origin_source_id: NonEmpty
    evidence_refs: Annotated[tuple[NonEmpty, ...], Field(min_length=1)]
    provisional_key: NonEmpty | None = None

    @model_validator(mode="after")
    def scoped_provisional_identity(self) -> Self:
        if self.identity_status == IdentityStatus.PROVISIONAL and self.provisional_key is None:
            raise ValueError("provisional identity requires a discriminating source-scoped key")
        if self.identity_status == IdentityStatus.RESOLVED and self.provisional_key is not None:
            raise ValueError("resolved identity cannot retain a provisional key")
        return self


class Snapshot(Contract):
    snapshot_id: NonEmpty
    fund_id: NonEmpty
    asof_date: PortfolioDate
    source_document_id: NonEmpty
    first_observed_at: UtcDatetime
    source_revision: Annotated[StrictInt, Field(ge=1, le=2**63 - 1)]
    parser_version: NonEmpty
    weight_basis: WeightBasis
    total_weight: ExactDecimal
    quality: SnapshotQuality
    supersedes_snapshot_id: NonEmpty | None = None

    @property
    def reported_residual(self) -> Decimal:
        """Exactly 1 - W; never a balancing holding, independent of Decimal context."""
        _, digits, exponent = self.total_weight.as_tuple()
        assert isinstance(exponent, int)
        precision = max(28, len(digits) + abs(exponent) + 2)
        with localcontext(Context(prec=precision, Emin=-999999, Emax=999999, clamp=0)):
            return Decimal("1") - self.total_weight

    @property
    def has_unit_total(self) -> bool:
        """Weight-only criterion; it does not assert full metric eligibility."""
        return self.reported_residual.copy_abs() <= Decimal("0.000000001")

    @model_validator(mode="after")
    def coherent_snapshot(self) -> Self:
        if self.supersedes_snapshot_id == self.snapshot_id:
            raise ValueError("a snapshot cannot supersede itself")
        reasons = set(self.quality.reasons)
        if not self.has_unit_total and QualityReason.WEIGHT_RESIDUAL not in reasons:
            raise ValueError("a non-unit total requires an explicit residual reason")
        if self.weight_basis == WeightBasis.UNKNOWN:
            if QualityReason.AMBIGUOUS_WEIGHT_BASIS not in reasons:
                raise ValueError("an unknown denominator requires an explicit reason")
        if self.quality.disposition == Disposition.ELIGIBLE:
            if self.reported_residual.copy_abs() > Decimal("0.01"):
                raise ValueError("material unexplained residual requires quarantine")
        return self
