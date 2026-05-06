"""
Tests for EmbeddingMetadata schema-version resolution.

The version is derived from provenance state, not declared:
  source_sha256 present  -> v2
  source_sha256 absent   -> v1
A declared schema_version that disagrees with the derived value raises.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from nova.core.provenance import compute_source_sha256
from nova.core.schemas import EmbeddingMetadata


def _base_kwargs(**overrides):
    kw = dict(
        model="nomic-embed-text:v1.5",
        dim=768,
        vector=[0.1] * 768,
        source_text="hello world",
        generated_at=datetime.now(timezone.utc),
    )
    kw.update(overrides)
    return kw


# ---------------------------------------------------------------------------
# Derived version rule
# ---------------------------------------------------------------------------

def test_legacy_record_resolves_to_v1():
    m = EmbeddingMetadata(**_base_kwargs())
    assert m.schema_version == 1
    assert m.source_sha256 is None
    assert m._verification_status == "skipped"


def test_record_with_hash_resolves_to_v2():
    sha = compute_source_sha256("hello world")
    m = EmbeddingMetadata(**_base_kwargs(source_sha256=sha))
    assert m.schema_version == 2
    assert m.source_sha256 == sha


def test_explicit_v1_with_no_hash_is_accepted():
    m = EmbeddingMetadata(**_base_kwargs(schema_version=1))
    assert m.schema_version == 1


def test_explicit_v2_with_hash_is_accepted():
    sha = compute_source_sha256("hello world")
    m = EmbeddingMetadata(**_base_kwargs(schema_version=2, source_sha256=sha))
    assert m.schema_version == 2


# ---------------------------------------------------------------------------
# Mismatch detection
# ---------------------------------------------------------------------------

def test_declared_v2_without_hash_raises():
    with pytest.raises(ValidationError) as exc:
        EmbeddingMetadata(**_base_kwargs(schema_version=2))
    assert "schema_version mismatch" in str(exc.value)


def test_declared_v1_with_hash_raises():
    sha = compute_source_sha256("hello world")
    with pytest.raises(ValidationError) as exc:
        EmbeddingMetadata(**_base_kwargs(schema_version=1, source_sha256=sha))
    assert "schema_version mismatch" in str(exc.value)


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------

def test_round_trip_v1_preserves_shape():
    m = EmbeddingMetadata(**_base_kwargs())
    dumped = m.model_dump()
    assert "_verification_status" not in dumped
    restored = EmbeddingMetadata(**dumped)
    assert restored.schema_version == 1
    assert restored.source_sha256 is None


def test_round_trip_v2_preserves_shape():
    sha = compute_source_sha256("hello world")
    m = EmbeddingMetadata(**_base_kwargs(source_sha256=sha))
    dumped = m.model_dump()
    assert "_verification_status" not in dumped
    assert dumped["schema_version"] == 2
    assert dumped["source_sha256"] == sha
    restored = EmbeddingMetadata(**dumped)
    assert restored.schema_version == 2
    assert restored.source_sha256 == sha


def test_private_attr_does_not_serialize():
    sha = compute_source_sha256("hello world")
    m = EmbeddingMetadata(**_base_kwargs(source_sha256=sha))
    m._verification_status = "ok"  # pretend verification ran
    dumped = m.model_dump()
    assert "_verification_status" not in dumped
    # And model_dump_json too, for paranoia.
    assert "_verification_status" not in m.model_dump_json()


# ---------------------------------------------------------------------------
# Other existing invariants we don't want to regress
# ---------------------------------------------------------------------------

def test_dim_must_match_vector_length():
    with pytest.raises(ValueError, match="vector length"):
        EmbeddingMetadata(**_base_kwargs(dim=512))  # vector is len 768


def test_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        EmbeddingMetadata(**_base_kwargs(unexpected_field="boom"))
