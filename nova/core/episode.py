"""
nova/core/episode.py — Tier 1 Episode primitive.

Per ADR-134: episodes are immutable, content-addressed units of experience.
The hash is computed over canonical JSON of all semantic fields and serves
as both identity and tamper-detection.

Frozen dataclass: mutation raises FrozenInstanceError.
Hash is deterministic across processes (sorted keys, no whitespace).
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


def _utcnow_iso() -> str:
    """ISO-8601 UTC timestamp, second precision, Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class Episode:
    """
    An immutable episodic record.

    Fields:
        timestamp: ISO-8601 UTC, set at construction if not provided.
        kind:      short tag, e.g. "dialogue", "reflection", "observation".
        content:   the semantic payload (free-form string).
        context:   optional structured metadata (dict).
        hash:      SHA-256 over canonical JSON of the above. Auto-computed.

    The hash field is set in __post_init__ via object.__setattr__
    (the only sanctioned escape hatch for frozen dataclasses).
    """
    timestamp: str = field(default_factory=_utcnow_iso)
    kind: str = "observation"
    content: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    hash: str = ""

    def __post_init__(self) -> None:
        if not self.hash:
            object.__setattr__(self, "hash", self._compute_hash())

    @staticmethod
    def _nfc(obj: Any) -> Any:
        """Recursively NFC-normalize all strings in a JSON-compatible structure."""
        if isinstance(obj, str):
            return unicodedata.normalize("NFC", obj)
        if isinstance(obj, dict):
            return {Episode._nfc(k): Episode._nfc(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [Episode._nfc(v) for v in obj]
        return obj

    def _canonical_payload(self) -> str:
        """Canonical JSON: NFC-normalized, sorted keys, no whitespace, hash excluded."""
        payload = {
            "timestamp": self._nfc(self.timestamp),
            "kind": self._nfc(self.kind),
            "content": self._nfc(self.content),
            "context": self._nfc(self.context),
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def _compute_hash(self) -> str:
        return hashlib.sha256(self._canonical_payload().encode("utf-8")).hexdigest()

    def verify(self) -> bool:
        """Return True iff the stored hash matches the current content."""
        return self.hash == self._compute_hash()

    def to_dict(self) -> dict[str, Any]:
        """Plain dict, suitable for JSON serialization or DB insertion."""
        return asdict(self)
