# M02 data contracts — schema 1.0.0

This implements the candidate-record and canonicalization part of specification
sections 6–8. It does not implement ingestion, database publication, historical
snapshot selection, or financial engines.

## Models and validation

The public model namespace is ledger.types. Its records are frozen Pydantic
models with unknown fields forbidden. Nested collections are tuples of immutable
values/models; existing model instances are revalidated rather than trusted.

| Model | Identity | Additional contract |
| --- | --- | --- |
| SourceDocument | document_id | Required source/fund identifiers, SHA-256 content hash, object reference, fetch time, content type and adapter version; optional publication time requires evidence and cannot follow fetch |
| Snapshot | snapshot_id | Required portfolio date, source document, first observation, positive revision, parser version, denominator, reported total and explicit quality states |
| Position | snapshot_id + position_id | Required instrument, source row/name, asset category and reported weight; original identifiers, quantity, market value, currency and diagnostic NAV weight retained |
| Instrument | instrument_id | Required source and evidence; provisional identities require a discriminating source-scoped key |

Identity allocation and cross-record references are not verified against a
database in this ticket. A source-scoped provisional key records evidence; these
models do not establish that the key actually identifies a unique security.

### Dates, timestamps and financial values

- Portfolio dates are date objects or YYYY-MM-DD strings. Timestamps and numeric
  epochs are rejected as portfolio dates.
- Knowledge timestamps accept aware datetime objects or ISO strings with an
  explicit Z or numeric offset. They normalize to UTC. Numeric epoch strings,
  naive times and unrepresentable UTC instants fail validation.
- Timestamp strings support at most six fractional-second digits, matching
  Arrow microseconds; excess precision is rejected rather than truncated.
- Financial values accept Decimal or decimal strings. Floats, booleans, integers,
  NaN and infinity are rejected. No rounding or normalization is applied.
- Decimal input has a storage/resource bound: at most 256 input characters,
  64 coefficient digits, and a decimal exponent between -64 and 64 inclusive.
  Values outside these bounds fail explicitly. This is an input-format limit,
  not a financial eligibility threshold.
- Trailing zeros and signed zero are preserved. Scientific notation uses an
  uppercase E regardless of the caller's Decimal context.
- Source revision is a strict integer in 1..2**63-1 to fit Arrow int64.
- Currency is an uppercase three-letter code shape. Adapters must establish the
  actual currency and source scope; a shape check is not an ISO registry lookup.

## Quality dimensions

SnapshotQuality keeps source completeness, identity coverage, classification
coverage, disposition, and explicit reasons separate. Incomplete or unknown
coverage must carry its corresponding reason. Known blocking reasons prevent an
eligible disposition.

Snapshot.reported_residual is exactly 1 minus total_weight, independent of
the caller's Decimal precision, exponent limits or clamp settings. A residual
outside 1e-9 requires a weight_residual reason. An absolute residual above 0.01
cannot be declared eligible. An unknown denominator also requires a blocking
reason. Values are never normalized and residuals are never assigned to cash.

Snapshot.has_unit_total tests only the weight total within 1e-9. It does not
establish identity coverage, source completeness, or full-overlap eligibility.

Position deliberately retains negative weights and unsupported asset categories
as candidate evidence. An individual model's validity is not permission to
publish that row for analytics. M05 must reconcile positions against their
snapshot and set the appropriate blocking reasons; M07 must enforce publication
eligibility. M02 does not claim those cross-row checks are complete.

## Arrow physical representation

ledger.arrow exposes schema_for, to_arrow and from_arrow for the four record
kinds. Schemas have explicit nullable fields, nested structs/list element types,
record-kind metadata, and schema-version metadata.

- Financial decimals use UTF-8 strings with logical-type metadata. A fixed-scale
  Arrow decimal would erase differing source precision. Revalidation reconstructs
  the exact Decimal value and scale.
- Dates use date32; timestamps use timestamp(us, UTC); revisions use int64.
- Enums use validated strings; immutable identifier/evidence tuples use Arrow
  lists and are restored on decoding.
- Readers reject unexpected/missing columns, changed physical types/nullability,
  absent/incompatible metadata, and invalid model values. They do not cast
  unknown tables into the requested schema or drop extra fields.
- Both directions reject duplicate record keys and wrong record kinds. Returned
  batches use deterministic primary-key order.

These functions operate on in-memory tables. File layout, Parquet writers,
storage I/O and schema migrations are subsequent work. PyArrow currently lacks
usable typing metadata in this environment; the mypy exception is limited to
that dependency, with runtime schema/roundtrip tests covering its boundary.

## Canonical records and hashes

ledger.canonical exposes canonical_records and hash_records. The former returns
UTF-8 JSON bytes; the latter is their SHA-256 hexadecimal digest.

The envelope contains hash_version=fund-ledger-records-v1, schema_version=1.0.0,
the explicit record_kind, and records sorted by the primary keys above. JSON
object keys are sorted, whitespace separators are fixed, and nested tuple order
is preserved. Different record kinds have different empty-batch hashes.

Models are revalidated before serialization, including instances made through
Pydantic's unchecked construction/copy methods. Duplicate keys are errors even
when the duplicate rows have identical values.

Source precision is part of identity: 0.4 and 0.4000 intentionally produce
different record hashes. Reordering records or supplying equivalent timestamp
offsets does not change a hash. Changing a material value, record kind or
schema/hash version does.

This is a canonical-record hash, not data_version. The specification's
data_version covers the physical dataset manifest and object hashes; its
publication contract remains M07. A canonical-format change must introduce a
new hash/schema version rather than silently changing the meaning of old hashes.

## Verification scope

Tests were written before the missing modules were implemented and initially
failed to import those modules. Additional failing regressions exposed and fixed
Decimal-context dependence and UTC-boundary overflow.

The suite covers all four JSON/Arrow round trips, exact optional evidence and
numeric fields, required provenance, source quality state consistency, immutable
nesting/revalidation, duplicate identities, a fixed interoperability hash vector,
row permutations, randomized decimal values/scales, and Decimal-context changes.
Existing v1.0 golden fixture expectations are unchanged.
