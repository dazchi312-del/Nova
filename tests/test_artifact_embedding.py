"""
Smoke tests for EmbeddingMetadata schema and RichArtifact integration.

Verifies:
- Dim assertion catches mismatched vector lengths
- RichArtifact accepts/serializes embedding correctly
- to_dict(include_vector) flag works
- extract_embedding_source() handles text + binary
"""

import pytest
from datetime import datetime

from nova.core.artifact import (
    EmbeddingMetadata,
    RichArtifact,
    ArtifactDomain,
    ShapeDescriptor,
    NOMIC_EMBED_DIM,
    NOMIC_MODEL_NAME,
    EMBED_SOURCE_MAX_CHARS,
    extract_embedding_source,
    enrich_artifact,
    infer_domain,
)


# ---------- EmbeddingMetadata ----------

def test_embedding_metadata_valid():
    """Correct dim passes __post_init__."""
    vec = [0.1] * NOMIC_EMBED_DIM
    em = EmbeddingMetadata(
        vector=vec,
        model=NOMIC_MODEL_NAME,
        dim=NOMIC_EMBED_DIM,
        source_text="hello world",
    )
    assert em.dim == 768
    assert len(em.vector) == 768
    assert em.model == "nomic-embed-text-v1.5"
    assert isinstance(em.generated_at, datetime)


def test_embedding_metadata_dim_mismatch_raises():
    """Mismatched vector length raises ValueError."""
    with pytest.raises(ValueError, match="dim mismatch"):
        EmbeddingMetadata(
            vector=[0.1] * 512,  # wrong dim
            model=NOMIC_MODEL_NAME,
            dim=NOMIC_EMBED_DIM,
            source_text="oops",
        )


def test_embedding_metadata_empty_vector_raises():
    """Empty vector with non-zero dim fails."""
    with pytest.raises(ValueError, match="dim mismatch"):
        EmbeddingMetadata(
            vector=[],
            model=NOMIC_MODEL_NAME,
            dim=NOMIC_EMBED_DIM,
            source_text="",
        )


# ---------- RichArtifact integration ----------

def test_rich_artifact_without_embedding():
    """Default RichArtifact has embedding=None."""
    art = RichArtifact(
        name="test.py",
        content=b"def foo(): pass",
        domain=ArtifactDomain.CODE,
    )
    assert art.embedding is None
    d = art.to_dict()
    assert d["embedding"] is None


def test_rich_artifact_with_embedding():
    """RichArtifact carries embedding through to_dict."""
    em = EmbeddingMetadata(
        vector=[0.1] * NOMIC_EMBED_DIM,
        model=NOMIC_MODEL_NAME,
        dim=NOMIC_EMBED_DIM,
        source_text="def foo(): pass",
    )
    art = RichArtifact(
        name="test.py",
        content=b"def foo(): pass",
        domain=ArtifactDomain.CODE,
        embedding=em,
    )
    d = art.to_dict()
    assert d["embedding"] is not None
    assert d["embedding"]["model"] == NOMIC_MODEL_NAME
    assert d["embedding"]["dim"] == NOMIC_EMBED_DIM
    assert d["embedding"]["source_text"] == "def foo(): pass"
    assert "vector" not in d["embedding"]  # excluded by default


def test_to_dict_include_vector():
    """include_vector=True surfaces full vector."""
    vec = [0.1] * NOMIC_EMBED_DIM
    em = EmbeddingMetadata(
        vector=vec,
        model=NOMIC_MODEL_NAME,
        dim=NOMIC_EMBED_DIM,
        source_text="hi",
    )
    art = RichArtifact(
        name="x.txt",
        content=b"hi",
        domain=ArtifactDomain.TEXT,
        embedding=em,
    )
    d = art.to_dict(include_vector=True)
    assert "vector" in d["embedding"]
    assert len(d["embedding"]["vector"]) == NOMIC_EMBED_DIM


# ---------- extract_embedding_source ----------

def test_extract_embedding_source_text():
    """UTF-8 text decoded cleanly."""
    content = b"hello world"
    src = extract_embedding_source(content)
    assert src == "hello world"


def test_extract_embedding_source_truncates():
    """Long content truncated to max_chars."""
    content = b"a" * 5000
    src = extract_embedding_source(content)
    assert len(src) == EMBED_SOURCE_MAX_CHARS
    assert src == "a" * EMBED_SOURCE_MAX_CHARS


def test_extract_embedding_source_custom_max():
    """Custom max_chars respected."""
    content = b"abcdefghij"
    src = extract_embedding_source(content, max_chars=4)
    assert src == "abcd"


def test_extract_embedding_source_binary_safe():
    """Binary content does not raise (errors='ignore')."""
    content = bytes([0xFF, 0xFE, 0xFD, 0xFC])
    src = extract_embedding_source(content)
    # may be empty or partial; key requirement: no exception
    assert isinstance(src, str)


# ---------- enrich_artifact pass-through ----------

def test_enrich_artifact_no_embedding():
    """enrich_artifact does not populate embedding (deferred to embedder)."""
    art = enrich_artifact("foo.py", b"def bar(): return 42")
    assert art.embedding is None
    assert art.domain == ArtifactDomain.CODE


# ---------- Sanity: constants ----------

def test_constants():
    assert NOMIC_EMBED_DIM == 768
    assert NOMIC_MODEL_NAME == "nomic-embed-text-v1.5"
    assert EMBED_SOURCE_MAX_CHARS == 2000
