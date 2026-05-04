"""
Artifact schema for Phase 9 Imagination Engine.

Artifacts carry structural metadata enabling cross-domain resonance detection.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Any
from enum import Enum
from datetime import datetime

if TYPE_CHECKING:
    from nova.core.embedder import NomicEmbedder

# EmbeddingMetadata is canonical in nova.core.schemas (Pydantic).
# Re-exported here for backward-compatible imports.
from nova.core.schemas import EmbeddingMetadata, ShapeDescriptor, StructuralMetadata
from nova.core.extractors.base import ExtractionResult
from nova.core.extractors.python_ast import PythonASTExtractor


# Embedding model constants
NOMIC_EMBED_DIM = 768
NOMIC_MODEL_NAME = "nomic-embed-text:v1.5"
EMBED_SOURCE_MAX_CHARS = 2000  # Path B: truncate content for embedding


class ArtifactDomain(Enum):
    """Primary domain classification."""
    CODE = "code"
    AUDIO = "audio"
    VISUAL = "visual"
    TEXT = "text"
    DATA = "data"
    UNKNOWN = "unknown"


@dataclass
class RichArtifact:
    """
    Extended artifact with structural metadata for cross-domain resonance.

    Wraps raw artifact bytes with shape descriptors and taste anchors.
    """
    name: str
    content: bytes
    domain: ArtifactDomain

    # Structural analysis (populated by _safe_extract for recognized types)
    shape: Optional[ShapeDescriptor] = None
    structure: Optional[StructuralMetadata] = None

    # Taste alignment
    anchors: list[str] = field(default_factory=list)  # refs to references.md
    resonance_score: float = 0.0  # 0-1, alignment with taste

    # Geometric similarity (Block D)
    embedding: Optional[EmbeddingMetadata] = None

    # Provenance
    created_at: datetime = field(default_factory=datetime.now)
    iteration_id: Optional[str] = None

    @property
    def size_bytes(self) -> int:
        return len(self.content)


def infer_domain(filename: str, content: bytes) -> ArtifactDomain:
    """Infer artifact domain from filename and content."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    code_exts = {"py", "js", "ts", "rs", "go", "c", "cpp", "h", "java"}
    audio_exts = {"wav", "mp3", "flac", "ogg", "aiff"}
    visual_exts = {"png", "jpg", "jpeg", "gif", "svg", "webp"}
    text_exts = {"txt", "md", "rst", "json", "yaml", "toml"}
    data_exts = {"csv", "parquet", "db", "sqlite"}

    if ext in code_exts:
        return ArtifactDomain.CODE
    if ext in audio_exts:
        return ArtifactDomain.AUDIO
    if ext in visual_exts:
        return ArtifactDomain.VISUAL
    if ext in text_exts:
        return ArtifactDomain.TEXT
    if ext in data_exts:
        return ArtifactDomain.DATA

    # Content-based fallback
    try:
        text = content.decode("utf-8")
        if "def " in text or "class " in text or "import " in text:
            return ArtifactDomain.CODE
        return ArtifactDomain.TEXT
    except UnicodeDecodeError:
        return ArtifactDomain.UNKNOWN


def extract_embedding_source(
    content: bytes,
    max_chars: int = EMBED_SOURCE_MAX_CHARS,
) -> str:
    """
    Path B: Extract truncated text for embedding.

    Decodes bytes with error tolerance, truncates to max_chars.
    Binary domains (audio/visual) will yield mostly empty/garbage strings —
    those should skip embedding at the call site.

    NOTE: Shape extraction is now wired into enrich_artifact() directly
    via _safe_extract(). This helper remains the text fallback for vector
    embeddings (orthogonal signal — embeddings encode intent, shape
    encodes organization).
    """
    try:
        text = content.decode("utf-8", errors="ignore")
    except Exception:
        return ""
    return text[:max_chars]


# Singleton extractor instance. Stateless; safe to share across calls.
_PY_AST_EXTRACTOR = PythonASTExtractor()


def _safe_extract(name: str, blob: bytes) -> ExtractionResult:
    """
    Best-effort shape/structure extraction. NEVER raises.

    Dispatches by file extension. Unknown types and all failures yield
    ExtractionResult(structure=None, shape=None) — extraction is
    metadata-augmentation, never a blocker for the imagination loop.
    """
    try:
        if name.endswith(".py"):
            return _PY_AST_EXTRACTOR.extract(name, blob)
        # Future: .md, .json, .yaml, .ts dispatch here.
        return ExtractionResult(structure=None, shape=None)
    except Exception:
        # Hard guarantee: extraction failure is non-fatal.
        return ExtractionResult(structure=None, shape=None)


def enrich_artifact(
    name: str,
    content: bytes,
    embedder: Optional["NomicEmbedder"] = None,
) -> RichArtifact:
    """
    Convert raw artifact to RichArtifact with inferred metadata.

    If an embedder is provided, attempts to populate `embedding` via
    Path B (truncated text source). Embedding failure is non-fatal:
    embedding remains None and the loop continues.

    Shape and structural metadata are populated via _safe_extract()
    when the file type is recognized (currently: Python). All extraction
    failures are silently swallowed — shape/structure remain None and
    the loop proceeds.
    """
    domain = infer_domain(name, content)

    embedding: Optional[EmbeddingMetadata] = None
    if embedder is not None:
        source = extract_embedding_source(content)
        if source.strip():
            embedding = embedder.embed(source)
            # embed() returns None on failure; that's fine, field stays None

    extraction = _safe_extract(name, content)

    return RichArtifact(
        name=name,
        content=content,
        domain=domain,
        shape=extraction.shape,
        structure=extraction.structure,
        anchors=[],
        resonance_score=0.0,
        embedding=embedding,
    )
