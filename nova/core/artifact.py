"""
Artifact schema for Phase 9 Imagination Engine.

Artifacts carry structural metadata enabling cross-domain resonance detection.
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum
from datetime import datetime


class ArtifactDomain(Enum):
    """Primary domain classification."""
    CODE = "code"
    AUDIO = "audio"
    VISUAL = "visual"
    TEXT = "text"
    DATA = "data"
    UNKNOWN = "unknown"


@dataclass
class ShapeDescriptor:
    """
    Structural shape extracted from artifact.
    
    These are domain-agnostic patterns that enable cross-domain matching.
    Examples: "repetition-with-variation", "negative-space", "compression"
    """
    primary: str                           # e.g., "layered-repetition"
    secondary: list[str] = field(default_factory=list)  # supporting shapes
    confidence: float = 0.0                # 0-1, how confident in extraction


@dataclass
class StructuralMetadata:
    """Domain-specific structural information."""
    
    # Code-specific
    ast_depth: Optional[int] = None
    cyclomatic_complexity: Optional[int] = None
    function_count: Optional[int] = None
    
    # Audio-specific (future)
    duration_s: Optional[float] = None
    frequency_range: Optional[tuple[float, float]] = None
    dynamic_range_db: Optional[float] = None
    
    # Visual-specific (future)
    dimensions: Optional[tuple[int, int]] = None
    color_palette_size: Optional[int] = None
    
    # Text-specific
    word_count: Optional[int] = None
    sentence_avg_length: Optional[float] = None
    
    # Generic
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class RichArtifact:
    """
    Extended artifact with structural metadata for cross-domain resonance.
    
    Wraps raw artifact bytes with shape descriptors and taste anchors.
    """
    name: str
    content: bytes
    domain: ArtifactDomain
    
    # Structural analysis
    shape: Optional[ShapeDescriptor] = None
    structure: Optional[StructuralMetadata] = None
    
    # Taste alignment
    anchors: list[str] = field(default_factory=list)  # refs to references.md
    resonance_score: float = 0.0  # 0-1, alignment with taste
    
    # Provenance
    created_at: datetime = field(default_factory=datetime.now)
    iteration_id: Optional[str] = None
    
    @property
    def size_bytes(self) -> int:
        return len(self.content)
    
    def to_dict(self) -> dict:
        """Serialize for storage/API."""
        return {
            "name": self.name,
            "domain": self.domain.value,
            "size_bytes": self.size_bytes,
            "shape": {
                "primary": self.shape.primary,
                "secondary": self.shape.secondary,
                "confidence": self.shape.confidence
            } if self.shape else None,
            "anchors": self.anchors,
            "resonance_score": self.resonance_score,
            "created_at": self.created_at.isoformat(),
            "iteration_id": self.iteration_id
        }


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


def enrich_artifact(name: str, content: bytes) -> RichArtifact:
    """
    Convert raw artifact to RichArtifact with inferred metadata.
    
    Shape extraction is deferred to Phase 9 full implementation.
    """
    domain = infer_domain(name, content)
    
    return RichArtifact(
        name=name,
        content=content,
        domain=domain,
        shape=None,  # TODO: Phase 9 shape extraction
        structure=None,  # TODO: Phase 9 structural analysis
        anchors=[],
        resonance_score=0.0
    )
