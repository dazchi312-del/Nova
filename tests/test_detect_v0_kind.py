# tests/test_detect_v0_kind.py
import json
from pathlib import Path

import pytest

from nova.migration.detect import (
    AmbiguousRecordError,
    UnclassifiableRecordError,
    detect_v0_kind,
)

FIXTURES_ROOT = Path(__file__).resolve().parent.parent / "nova" / "migration"


def load(relpath: str) -> dict:
    """Load a JSON fixture relative to nova/migration/."""
    return json.loads((FIXTURES_ROOT / relpath).read_text())


def test_summary_golden_fixture():
    rec = load("fixtures/v0/exp_summary_smoke_1777263238.json")
    assert detect_v0_kind(rec) == "experiment_summary"


def test_iteration_strong_keys():
    assert detect_v0_kind({"iteration_index": 0, "code_hash": "a" * 16}) == "iteration"


def test_ambiguous_raises():
    with pytest.raises(AmbiguousRecordError):
        detect_v0_kind({"best_iteration_index": 0, "iteration_index": 0})


def test_unclassifiable_raises():
    with pytest.raises(UnclassifiableRecordError):
        detect_v0_kind({"experiment_id": "x", "goal": "y"})


def test_weak_fallback_summary():
    # Has only weak signals; scores list-of-dicts → summary
    rec = {"experiment_id": "x", "scores": [{"iter": 1, "overall": 0.9}]}
    assert detect_v0_kind(rec) == "experiment_summary"
