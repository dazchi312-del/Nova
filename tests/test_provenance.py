"""
Tests for nova.core.provenance.

Locks in the SHA-256 contract and verify_embedding state machine.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from nova.core.provenance import compute_source_sha256, verify_embedding
from nova.core.schemas import EmbeddingMetadata


# ---------------------------------------------------------------------------
# compute_source_sha256: determinism and stability
# ---------------------------------------------------------------------------

def test_compute_source_sha256_known_vector():
    """Pinned digest. If this changes, the on-disk format has changed."""
    assert compute_source_sha256("hello world") == (
        "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    )


def test_compute_source_sha256_empty_string():
    assert compute_source_sha256("") == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_compute_source_sha256_deterministic():
    src = "the quick brown fox " * 50
    assert compute_source_sha256(src) == compute_source_sha256(src)


def test_compute_source_sha256_unicode_utf8():
    """UTF-8 encoding is part of the contract."""
    # Same codepoints, encoded as UTF-8, must produce stable digest.
    src = "café — 日本語 — 🦊"
    expected = compute_source_sha256(src)
    assert compute_source_sha256(src) == expected
    # Sanity: differs from a visually-similar ASCII string.
    assert compute_source_sha256("cafe") != expected


# ---------------------------------------------------------------------------
# verify_embedding: state machine
# ---------------------------------------------------------------------------

def _make_v2_record(source_text: str = "canonical source", *, hash_override: str | None = None) -> EmbeddingMetadata:
    sha = hash_override if hash_override is not None else compute_source_sha256(source_text)
    return EmbeddingMetadata(
        model="nomic-embed-text:v1.5",
        dim=768,
        vector=[0.1] * 768,
        source_text=source_text,
        source_sha256=sha,
        generated_at=datetime.now(timezone.utc),
    )


def _make_v1_record(source_text: str = "legacy source") -> EmbeddingMetadata:
    # v1 == no source_sha256; derived rule sets schema_version=1.
    return EmbeddingMetadata(
        model="nomic-embed-text:v1.5",
        dim=768,
        vector=[0.1] * 768,
        source_text=source_text,
        generated_at=datetime.now(timezone.utc),
    )


def test_verify_ok_when_hash_matches():
    m = _make_v2_record("hello world")
    assert verify_embedding(m) == "ok"
    assert m._verification_status == "ok"


def test_verify_mismatch_when_source_differs(caplog):
    m = _make_v2_record("hello world")
    # Tamper with source_text after construction; hash is now stale.
    m.source_text = "goodbye world"
    with caplog.at_level("WARNING"):
        result = verify_embedding(m)
    assert result == "mismatch"
    assert m._verification_status == "mismatch"
    assert any("mismatch" in rec.message for rec in caplog.records)


def test_verify_mismatch_when_hash_is_wrong():
    """Producer lied about the hash."""
    bogus = "0" * 64
    m = _make_v2_record("hello world", hash_override=bogus)
    assert verify_embedding(m) == "mismatch"
    assert m._verification_status == "mismatch"


def test_verify_skipped_for_v1_record():
    m = _make_v1_record()
    assert verify_embedding(m) == "skipped"
    assert m._verification_status == "skipped"


def test_verify_never_raises_on_pathological_text():
    """Verifier must not raise; it returns a status."""
    m = _make_v2_record("\x00\x01\x02 weird \uffff control")
    # Should still match because we hashed the same string.
    assert verify_embedding(m) == "ok"


def test_verify_status_starts_skipped_before_call():
    m = _make_v2_record("hello world")
    assert m._verification_status == "skipped"  # default from PrivateAttr
