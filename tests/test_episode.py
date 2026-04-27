"""
Tests for nova.core.episode — Tier 1 immutable primitive.

Three core properties (formalized from S31 verification):
  1. Determinism   — identical inputs produce identical hashes
  2. Immutability  — frozen dataclass rejects all mutation
  3. Tamper detect — verify() catches forced mutation via object.__setattr__

Plus edge cases: unicode, nested context, large payloads, type distinctions,
key-order independence (canonical JSON).
"""
import pytest
from dataclasses import FrozenInstanceError
from nova.core.episode import Episode


# ---------- Core property 1: Determinism ----------

class TestDeterminism:
    def test_same_inputs_same_hash(self):
        e1 = Episode(timestamp="2026-04-25T00:00:00Z", content="hello", context={"k": "v"})
        e2 = Episode(timestamp="2026-04-25T00:00:00Z", content="hello", context={"k": "v"})
        assert e1.hash == e2.hash

    def test_different_content_different_hash(self):
        e1 = Episode(timestamp="2026-04-25T00:00:00Z", content="hello", context={})
        e2 = Episode(timestamp="2026-04-25T00:00:00Z", content="world", context={})
        assert e1.hash != e2.hash

    def test_key_order_independence(self):
        """Canonical JSON: insertion order of context keys must not affect hash."""
        e1 = Episode(timestamp="t", content="c", context={"a": 1, "b": 2})
        e2 = Episode(timestamp="t", content="c", context={"b": 2, "a": 1})
        assert e1.hash == e2.hash


# ---------- Core property 2: Immutability ----------

class TestImmutability:
    def test_timestamp_frozen(self):
        e = Episode(timestamp="t", content="c", context={})
        with pytest.raises(FrozenInstanceError):
            e.timestamp = "other"

    def test_content_frozen(self):
        e = Episode(timestamp="t", content="c", context={})
        with pytest.raises(FrozenInstanceError):
            e.content = "other"

    def test_context_frozen(self):
        e = Episode(timestamp="t", content="c", context={})
        with pytest.raises(FrozenInstanceError):
            e.context = {"new": "dict"}

    def test_hash_frozen(self):
        e = Episode(timestamp="t", content="c", context={})
        with pytest.raises(FrozenInstanceError):
            e.hash = "fake"


# ---------- Core property 3: Tamper detection ----------

class TestTamperDetection:
    def test_verify_passes_for_untouched(self):
        e = Episode(timestamp="t", content="c", context={"k": "v"})
        assert e.verify() is True

    def test_verify_fails_after_forced_mutation(self):
        """object.__setattr__ bypasses frozen — verify() must catch it."""
        e = Episode(timestamp="t", content="c", context={})
        object.__setattr__(e, "content", "tampered")
        assert e.verify() is False


# ---------- Edge cases ----------

class TestEdgeCases:
    def test_empty_content(self):
        e = Episode(timestamp="t", content="", context={})
        assert e.verify() is True
        assert len(e.hash) == 64  # SHA-256 hex

    def test_empty_context(self):
        e = Episode(timestamp="t", content="c", context={})
        assert e.verify() is True

    def test_unicode_content(self):
        # Mix: emoji, CJK, RTL, combining marks
        e = Episode(timestamp="t", content="café 你好 🌌 שלום", context={})
        assert e.verify() is True

    def test_unicode_in_context(self):
        e = Episode(timestamp="t", content="c", context={"日本語": "値", "emoji": "🔑"})
        assert e.verify() is True

    def test_nested_context(self):
        ctx = {
            "outer": {"inner": {"deep": [1, 2, {"deeper": "value"}]}},
            "list": [1, "two", 3.0, None, True],
        }
        e = Episode(timestamp="t", content="c", context=ctx)
        assert e.verify() is True

    def test_large_content(self):
        big = "x" * (1024 * 1024)  # 1 MB
        e = Episode(timestamp="t", content=big, context={})
        assert e.verify() is True
        assert len(e.hash) == 64

    def test_type_distinction_int_vs_float(self):
        """JSON preserves 1 vs 1.0 — hashes must differ."""
        e1 = Episode(timestamp="t", content="c", context={"n": 1})
        e2 = Episode(timestamp="t", content="c", context={"n": 1.0})
        # Note: json.dumps(1) == "1", json.dumps(1.0) == "1.0" — distinct.
        assert e1.hash != e2.hash

    def test_type_distinction_int_vs_string(self):
        e1 = Episode(timestamp="t", content="c", context={"n": 1})
        e2 = Episode(timestamp="t", content="c", context={"n": "1"})
        assert e1.hash != e2.hash

    def test_null_in_context(self):
        e = Episode(timestamp="t", content="c", context={"key": None})
        assert e.verify() is True


class TestKindField:
    def test_different_kind_different_hash(self):
        """`kind` participates in the canonical payload."""
        e1 = Episode(timestamp="t", kind="dialogue", content="c", context={})
        e2 = Episode(timestamp="t", kind="reflection", content="c", context={})
        assert e1.hash != e2.hash

    def test_default_kind_is_observation(self):
        e = Episode(timestamp="t", content="c", context={})
        assert e.kind == "observation"


class TestDefaultTimestamp:
    def test_default_timestamp_auto_set(self):
        """No-arg construction produces a valid ISO-8601 Z timestamp."""
        e = Episode(content="c")
        assert e.timestamp.endswith("Z")
        assert "T" in e.timestamp
        assert e.verify() is True


class TestNFCNormalization:
    def test_nfc_equals_nfd(self):
        """NFC 'é' (U+00E9) and NFD 'é' (U+0065 U+0301) hash identically."""
        nfc = "café"  # U+00E9
        nfd = "cafe\u0301"  # U+0065 + combining acute
        assert nfc != nfd  # bytewise distinct
        e1 = Episode(timestamp="t", content=nfc, context={})
        e2 = Episode(timestamp="t", content=nfd, context={})
        assert e1.hash == e2.hash

    def test_nfc_in_context_keys_and_values(self):
        e1 = Episode(timestamp="t", content="x", context={"café": "naïve"})
        e2 = Episode(timestamp="t", content="x",
                     context={"cafe\u0301": "nai\u0308ve"})
        assert e1.hash == e2.hash
