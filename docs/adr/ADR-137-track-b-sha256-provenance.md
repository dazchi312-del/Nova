# ADR-137: Track B — SHA-256 Provenance for Embedding Artifacts

**Status:** Accepted
**Date:** 2026-05-05  
**Phase:** 10, Step 4b
**Related commits:** `2dbf262` (implementation), `d52ac75` (documentation)
**Supersedes:** —
**Superseded by:** —

## Context

Phase 10 introduced persistent embedding artifacts as the substrate for Nova's
imagination engine: every embedded source text is captured alongside its vector,
metadata, and provenance. Track A established the artifact schema and writer.

Track B addresses a question Track A left open: **how do we know, weeks or months
later, that a stored embedding still corresponds to the source text we think it
does?**

The risks are concrete:

1. **Silent source drift.** A record's `source_text` field could be edited
   (manually, by a migration script, by a bug) without invalidating the vector,
   leaving us with a vector that no longer reflects its claimed input.
2. **Replay ambiguity.** When regenerating embeddings to compare model versions
   or debug retrieval, we need to confirm we're feeding the model the *exact*
   bytes it saw originally — not a re-tokenized, re-encoded, or re-truncated
   variant.
3. **Schema evolution without a tripwire.** As the artifact schema evolves
   (v1 → v2 → v3), we need a structural mechanism that distinguishes "old record,
   no provenance" from "new record, provenance broken."

We considered three options:

- **(A) Hash the full source text before any preprocessing.** Rejected: the
  embedder applies a 2000-character truncation, so a hash of the pre-truncation
  text would not let us verify what the model actually saw.
- **(B) Hash the post-truncation text the model sees.** Accepted. This makes the
  hash a faithful witness to the model's input.
- **(C) Hash the vector itself.** Rejected: vectors are deterministic outputs of
  (model, input), so hashing them conflates source identity with model identity
  and breaks under any model upgrade.

## Decision

We adopt option B and lock it structurally:

### 1. Hash function and scope

- SHA-256 of the UTF-8 bytes of the **post-truncation source text** — i.e., the
  exact string passed to the embedding model.
- Implemented as `compute_source_sha256(text: str) -> str` in
  `nova/core/provenance.py`.
- Truncation boundary (currently 2000 chars) is owned by the embedder and tested
  in `tests/test_embedder.py`. The hash sees whatever the model sees, by
  construction.

### 2. Schema version derivation

- `EmbeddingArtifact.schema_version` is **derived**, not declared by the writer.
- A record with a `source_sha256` field is v2; without it, v1.
- Pydantic validators in `nova/core/schemas/artifact.py` enforce:
  - v2 records MUST carry both `source_sha256` and `source_text`.
  - v1 records MUST NOT carry `source_sha256`.
  - `extra = "forbid"` to prevent silent field drift.
  - `dim` must match `len(vector)`.

This means a writer cannot accidentally produce a "v2 record with a missing
hash" — the schema rejects it at validation time.

### 3. Verification semantics

- `verify_embedding(artifact) -> Literal["ok", "mismatch", "skipped"]` in
  `nova/core/provenance.py`.
- Returns `"skipped"` for v1 records (no hash to verify).
- Returns `"ok"` if the recomputed hash of `source_text` equals
  `source_sha256`.
- Returns `"mismatch"` otherwise.
- **Never raises.** Verification is a diagnostic, not a control-flow gate.
  Callers (CI, replay tooling, future migration scripts) decide what to do with
  a mismatch.

### 4. Tooling

- `tools/replay_schema_check.py` walks a file or directory, validates every
  record against the schema, and runs `verify_embedding` on v2 records.
- Exit codes: `0` clean, `1` any mismatch or invalid record, `2` usage error.
- `--json` flag emits a structured summary + per-record list for CI parsing.

### 5. Deferred

- A `--require-v2` flag to fail on any v1 record. Deferred until v1 records have
  been migrated or aged out; introducing it now would create noisy CI on
  legitimately-old artifacts.

## Consequences

### Positive

- **Tamper-evident artifacts.** Any post-hoc edit to `source_text` produces a
  detectable mismatch.
- **Replay confidence.** `compute_source_sha256` is the canonical witness:
  re-embedding the stored `source_text` and re-hashing gives a bit-exact
  comparison point.
- **Structural correctness.** Schema version is a *consequence* of record
  contents, not a self-declared label, so the writer cannot lie about the
  version it produced.
- **No raise in verification.** Replay tooling can scan thousands of records
  and report comprehensively without aborting on the first bad record.
- **Locked by tests.** 29 tests across `tests/test_provenance.py`,
  `tests/test_schemas_legacy.py`, and `tests/test_embedder.py` (0.14s) prevent
  regression of the truncation-then-hash rule and the v1/v2 invariants.

### Negative / accepted costs

- **v1 records remain unverifiable.** This is intentional; we don't fabricate
  hashes for legacy records. Migration is a separate concern.
- **Hash is tied to the truncation boundary.** Changing the truncation length
  in the embedder is a breaking change for verification: old hashes will not
  match new truncations of the same source. This is the correct behavior — a
  truncation change *is* an input change — but it must be flagged in any future
  ADR that touches the embedder.
- **No provenance for the model itself.** A v2 record proves the source text
  was preserved; it does not prove which embedding model produced the vector.
  Model provenance is out of scope for Track B and a candidate for Track C.

### Follow-ups

- Migration plan for existing v1 records (re-embed and re-hash, or accept as
  permanently v1).
- `--require-v2` flag in `replay_schema_check.py` once migration completes.
- Track C: model provenance (model name, version, parameter hash) attached to
  each artifact.

## References

- `nova/core/provenance.py` — `compute_source_sha256`, `verify_embedding`
- `nova/core/schemas/artifact.py` — `EmbeddingArtifact`, validators
- `nova/core/embedder.py` — truncation boundary, hash invocation
- `tools/replay_schema_check.py` — batch verification tool
- `tests/test_provenance.py`, `tests/test_schemas_legacy.py`,
  `tests/test_embedder.py` — 29 tests, 0.14s
