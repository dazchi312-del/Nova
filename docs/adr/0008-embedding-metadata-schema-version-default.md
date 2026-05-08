# ADR-0008: EmbeddingMetadata.schema_version default is vestigial

- Status: Accepted (deferred implementation)
- Date: 2025-11-15
- Deciders: Nova Imagination Engine maintainers

## Context

EmbeddingMetadata.schema_version is declared with a default of 2.

The default value of 2 was set when source_sha256 was added as a
required-when-present provenance field. In practice, the field is now
populated by the embedder at write time and validated at read time. The
default is never the correct value for a freshly constructed record
that lacks provenance: such records should either fail validation or
be explicitly marked as legacy.

The default therefore serves no live purpose. It exists only as a
backstop for test fixtures and ad-hoc construction sites that predate
Phase 10.

## Decision

Change the declaration to use Optional[int] with a default of None.

Defer the implementation until the v0 to v1 corpus migration rewriter
lands. Implementing now would require auditing every test fixture and
construction site in the same commit, which conflicts with the
in-flight migration work.

When implemented, the change must be paired with:

1. A migration pass that backfills schema_version on existing
   in-memory records before serialization.
2. A validator update that rejects None at persistence boundaries.
3. Test fixture audit to ensure no fixture relies on the implicit 2.

## Consequences

Positive:

- Removes false-coupling between EmbeddingMetadata version axis and
  default-construction ergonomics.
- Forces explicit version declaration at construction sites, surfacing
  any code path that constructs metadata without provenance intent.

Negative:

- Implementation is non-trivial; the audit surface is wider than the
  one-line type change suggests.
- Until implemented, the inline TODO in nova/core/schemas.py remains
  the canonical reminder.

## Follow-ups

- Inline TODO in nova/core/schemas.py references this ADR.
- Implementation tracked as a Phase 10 follow-up, gated on the v0 to v1
  rewriter landing.
- ADR-0007 covers the parallel decision to keep both schema_version
  axes named identically.
