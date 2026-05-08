# nova/migration/detect.py
from typing import Any, Literal

RecordKind = Literal["iteration", "experiment_summary"]

# Strong signals — presence of any one is conclusive.
SUMMARY_STRONG = frozenset({
    "best_iteration_index",
    "stopped_reason",
    "iteration_count",
})

ITERATION_STRONG = frozenset({
    "iteration_index",
    "code_hash",
    "critique_applied",
    "artifacts",
    "sandbox_stdout",
    "sandbox_stderr",
})

# Weak signals — shared between kinds; used only as tiebreakers.
WEAK_SHARED = frozenset({
    "experiment_id",
    "goal",
    "scores",
    "final_score",
})


def detect_v0_kind(record: dict[str, Any]) -> RecordKind:
    """
    Classify a v0 record as 'iteration' or 'experiment_summary'.

    Rules (in order):
      1. If any SUMMARY_STRONG key is present and no ITERATION_STRONG → summary.
      2. If any ITERATION_STRONG key is present and no SUMMARY_STRONG → iteration.
      3. Conflict (both kinds of strong keys) → raise AmbiguousRecordError.
      4. No strong signals → fall back: 'scores' as a list-of-dicts implies summary;
         'iter' or 'overall' at top level implies iteration; else raise.
    """
    keys = set(record.keys())
    has_summary = bool(keys & SUMMARY_STRONG)
    has_iter = bool(keys & ITERATION_STRONG)

    if has_summary and not has_iter:
        return "experiment_summary"
    if has_iter and not has_summary:
        return "iteration"
    if has_summary and has_iter:
        raise AmbiguousRecordError(
            f"Record has both summary and iteration strong keys: "
            f"summary={keys & SUMMARY_STRONG}, iteration={keys & ITERATION_STRONG}"
        )

    # Weak fallback
    scores = record.get("scores")
    if isinstance(scores, list) and scores and isinstance(scores[0], dict):
        return "experiment_summary"
    if "iter" in keys or "overall" in keys:
        return "iteration"

    raise UnclassifiableRecordError(
        f"No discriminating keys found. Top-level keys: {sorted(keys)}"
    )


class AmbiguousRecordError(ValueError):
    pass


class UnclassifiableRecordError(ValueError):
    pass
