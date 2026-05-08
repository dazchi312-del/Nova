# ADR-0007: Two independent `schema_version` axes coexist by design

- Status: Accepted
- Date: 2025-11-15
- Deciders: Nova Imagination Engine maintainers

## Context

The Nova corpus persists `IterationRecord` objects (defined in
`nova/core/schemas.py`) that contain a nested `EmbeddingMetadata`
sub-record. Both models carry a field literally named `schema_version`,
with disjoint semantics and disjoint value spaces:

| Model              | Values | Meaning                                    | Source of truth                        |
|--------------------|--------|--------------------------------------------|----------------------------------------|
| IterationRecord    | 0, 1   | Top-level record format; 0 = legacy        | `nova/schema/constants.py`             |
| EmbeddingMetadata  | 1, 2   | Provenance presence; 2 = has source_sha256 | `nova/core/schemas.py` (inline)        |

The collision was discovered during Phase 10 Step 4b when adding the
v0→v1 migration rewriter. Both fields appear under the same key name
when records are serialized to JSON, distinguished only by structural
position (top-level vs. nested under `embedding`).

## Decision

Keep both fields named `schema_version`. Do not rename either at this
time. Disambiguation is by structural position and by package scope:

- `nova/schema/` is reserved for IterationRecord-level versioning truth.
- `nova/core/schemas.py` owns EmbeddingMetadata-level versioning inline.
- `nova/migration/` consumes `nova/schema/constants.py` only.

Docstrings in all three modules explicitly scope each axis (commit
`e5e95f5`).

## Consequences

**Positive**

- No on-disk format churn during active migration work.
- Existing 164-test suite passes unchanged.
- Sub-record versioning stays colocated with the model it versions.

**Negative**

- Future contributors must read scoping docstrings to avoid conflation.
- Tooling that grep-greps `schema_version` returns hits from both axes.

## Follow-ups

- ADR-0008 covers the `EmbeddingMetadata.schema_version` default-value
  cleanup.
- A future ADR may rename one or both fields once the v0→v1 corpus
  migration is complete and on-disk format changes are cheap again.
