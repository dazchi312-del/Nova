"""
nova.schema — IterationRecord v1 schema truth.

This package holds the canonical, permanent definitions for IterationRecord
schema versioning. It is deliberately scoped to the *top-level record* only.

Sub-record versioning (notably EmbeddingMetadata's v1/v2 axis tracking
SHA-256 provenance) lives in nova/core/schemas.py alongside the model
definition itself and is NOT re-exported from here.

For the migration rewriter that consumes these constants, see
nova/migration/migration_v0_to_v1.py.
"""

