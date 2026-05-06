"""
Provenance verification for Project Nova.

Ensures embeddings can be re-validated against their declared source.
Track B (SHA-256 Provenance), ADR pending.
"""

from __future__ import annotations

import hashlib
import logging

from nova.core.schemas import EmbeddingMetadata

log = logging.getLogger(__name__)


def compute_source_sha256(source_text: str) -> str:
    """Canonical hash function for embedding source text. UTF-8, SHA-256, hex."""
    return hashlib.sha256(source_text.encode("utf-8")).hexdigest()


def verify_embedding(meta: EmbeddingMetadata) -> str:
    """
    Verify that an embedding's stored source_text matches its declared sha256.

    Sets meta._verification_status as a side effect for in-memory introspection.
    Never raises: returns one of "ok" | "mismatch" | "skipped".

    - "skipped": legacy record (schema_version < 2) or hash absent.
    - "ok":     hash recomputes correctly.
    - "mismatch": stored source_text does not produce the declared hash.
                  Logged at WARNING; caller decides downstream policy.

    A "mismatch" indicates either (a) on-disk corruption of source_text,
    (b) a producer that lied about the hash, or (c) a bug in this verifier.
    None of those should be silently tolerated by analytical tooling, but
    none of them are fatal to loop progression — embeddings are enrichment.
    """
    if meta.schema_version < 2 or meta.source_sha256 is None:
        log.debug(
            "embedding verification skipped: schema_version=%d, sha=%s",
            meta.schema_version,
            "present" if meta.source_sha256 else "absent",
        )
        meta._verification_status = "skipped"
        return "skipped"

    actual = compute_source_sha256(meta.source_text)
    if actual == meta.source_sha256:
        meta._verification_status = "ok"
        return "ok"

    log.warning(
        "embedding source_sha256 mismatch: declared=%s actual=%s "
        "(model=%s dim=%d schema_version=%d)",
        meta.source_sha256,
        actual,
        meta.model,
        meta.dim,
        meta.schema_version,
    )
    meta._verification_status = "mismatch"
    return "mismatch"
