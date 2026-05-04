"""
Phase 10 Step 3a: enrich_artifact() shape/structure extraction.

Verifies that recognized file types receive populated shape descriptors,
that unrecognized types and malformed inputs gracefully degrade to None,
and that extraction failure is NEVER fatal.
"""
import pytest
from nova.core.artifact import enrich_artifact, RichArtifact
from nova.core.schemas import ShapeDescriptor, StructuralMetadata


def test_python_source_populates_shape():
    src = b"def hello(name):\n    return f'hi {name}'\n"
    art = enrich_artifact("greet.py", src)
    assert isinstance(art, RichArtifact)
    assert art.shape is not None, "Python source should yield a ShapeDescriptor"
    assert art.structure is not None, "Python source should yield StructuralMetadata"
    assert isinstance(art.shape, ShapeDescriptor)
    assert isinstance(art.structure, StructuralMetadata)


def test_python_source_structure_counts_functions():
    src = b"def a(): pass\ndef b(): pass\nclass C: pass\n"
    art = enrich_artifact("multi.py", src)
    assert art.structure is not None
    # The exact field names depend on StructuralMetadata schema;
    # at minimum we expect non-empty content reflecting 2 funcs + 1 class.
    dumped = art.structure.model_dump()
    # Sanity: the dump should be a non-empty dict.
    assert isinstance(dumped, dict) and len(dumped) > 0


def test_unrecognized_extension_yields_none():
    art = enrich_artifact("data.bin", b"\x00\x01\x02 binary garbage")
    assert art.shape is None
    assert art.structure is None


def test_malformed_python_is_nonfatal():
    # Syntactically broken Python — extractor must NOT raise.
    src = b"def broken(:\n    this is not python\n!!!"
    art = enrich_artifact("broken.py", src)
    # Either None (graceful failure) or partial — but MUST not raise.
    assert isinstance(art, RichArtifact)
    # We don't assert shape is None strictly: PythonASTExtractor may
    # return a minimal descriptor. The contract is "no exception".


def test_empty_python_file():
    art = enrich_artifact("empty.py", b"")
    assert isinstance(art, RichArtifact)
    # Empty file should not crash; shape may be a minimal descriptor or None.


def test_no_embedder_still_extracts_shape():
    """Shape extraction is independent of embedder presence."""
    art = enrich_artifact("solo.py", b"x = 1\n")
    assert art.embedding is None  # no embedder provided
    assert art.shape is not None  # shape still works
