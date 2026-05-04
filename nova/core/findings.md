# Nova Core — Technical Debt Findings

**Date:** 2025-05-02
**Phase:** 9 (Shape Extraction), Block D (Loop Integration)
**Context:** Discovered during legacy IP sweep prior to live loop verification.

---

## Finding 1: Dual Reflector Implementations

**Files:**
- `nova/core/loop.py` — inline `call_reflector` function (ACTIVE, line 240)
- `nova/core/reflector.py` — orphaned `Reflector` class (INACTIVE)

**Status:** `reflector.py` is not imported by the active dream loop. It contains
legacy IP `10.0.0.167` at lines 25 and 334.

**Risk:** Low. Dead code path. No runtime impact.

**Recommendation:** Defer cleanup until Phase 9 completion. When addressed,
either (a) delete `reflector.py` if confirmed unused, or (b) refactor inline
`call_reflector` into the class, ensuring ADR-136 anchor snapping (0.00, 0.50,
1.00) and ReflectorScore schema parity are preserved.

---

## Finding 2: Parallel Reflection Harness in dream_lab.py

**File:** `nova/core/dream_lab.py` (line 336)

**Status:** Self-contained `requests.post` call to `http://10.0.0.167:11434/api/generate`
with hardcoded `llama3.1:8b`. Not on the Block D execution path. `dream_lab` is
a downstream consumer of `loop.py` via `noe.py`.

**Risk:** Medium. Will fail if/when `dream_lab` is exercised, since both the IP
(10.0.0.167) and the model (llama3.1:8b) are no longer valid on the sovereign
lattice.

**Recommendation:** Patch when `dream_lab` is next activated. Update to
`http://192.168.100.2:11434/api/generate` and `phi4:latest`, OR refactor to call
the active `call_reflector` from `loop.py` to eliminate the third reflection
implementation.

---

## Finding 3: Embedder URL Construction Fragility

**File:** `nova/core/loop.py` (line 65), `NomicEmbedder.__init__`

**Status:** RESOLVED 2025-05-02. `LoopConfig.embedder_url` now holds base host
only; `NomicEmbedder` appends `/api/embed`. Pre-fix bug produced double-suffix
`/api/embed/api/embed`.

**Recommendation (preventive):** Add construction-time validation in
`NomicEmbedder.__init__` — reject URLs that already end in `/api/embed` or
contain `/api/`. Fail loud at construction, not at first request.

---

## Summary

| # | File | Severity | Blocker? | Action |
|---|------|----------|----------|--------|
| 1 | reflector.py | Low | No | Defer |
| 2 | dream_lab.py | Medium | No (Block D) | Patch when reactivated |
| 3 | loop.py embedder | — | Resolved | Add validator (preventive) |

---

## Finding 4: Tool Taxonomy — Two `replay_schema_check.py` Files

**Files:**
- `scripts/replay_schema_check.py` (TRACKED, commit 5ef73fe) — CANONICAL
- `tools/replay_schema_check.py` (UNTRACKED) — REFERENCE SKETCH

**Status:** Resolved 2026-05-04. The `scripts/` version is the Phase 9 bulk-sweep
validator: walks `experiments/*/`, validates per-iteration `iterNNN_record.json`
against `schema_v1`, cross-checks `summary.json`. It operates on the canonical
storage format and is the file to use.

The `tools/` version is an orphaned sketch implementing a trichotomy classifier
(FAIL / OK_NO_SHAPE / OK_WITH_SHAPE) targeting JSONL journals. The codebase
emits zero JSONL — confirmed via `grep -rn "jsonl" nova/core/`. The trichotomy
concept is valuable but its implementation targets a storage format that does
not exist in this project.

**Risk:** Low when documented; medium when undocumented (caused real confusion
this session — accidental overwrite during Step 4b work, recovered via
`git checkout`).

**Recommendation:** Keep `tools/` version untracked as a reference sketch.
Revisit only if/when JSONL emission becomes a real requirement. Do not add a
second tracked file with the same basename.

---

## Finding 5: Canonical Per-Iteration Storage Format

**Files:** `nova/core/loop.py`, `nova/core/artifact.py`

**Status:** Documented 2026-05-04. The dream loop writes per-experiment
directories with the following layout:

    experiments/<run_id>/
    ├── iter001_code.py
    ├── iter001_record.json
    ├── iter002_code.py
    ├── iter002_record.json
    ├── ...
    ├── final_code.py
    └── summary.json

All writes go through `_atomic_write` (write-to-temp + rename). No JSONL is
emitted anywhere in `nova/core/`. The `iterNNN_record.json` files conform to
`schema_v1` (see `nova/core/schemas.py::IterationRecord`). `summary.json`
aggregates the run-level metadata.

**Risk:** None — informational. Recorded to prevent repeat investigation of
"where do journals live?"

**Recommendation:** Treat this as the load-bearing storage contract. Any
schema migration must preserve this layout or define an explicit migration path.

---

## Finding 6: Phase 10 Step 4b Validation Evidence

**Commit:** `2dbf262` (2026-05-04)

**Status:** Validated. `enrich_artifact` shape extraction (via
`PythonASTExtractor`) and `IterationStatus` enum coercion are exercised by
`experiments/smoke_step4b_002/` — a 2-iteration run in which the Reflector
correctly penalized a matplotlib hallucination. All `iterNNN_record.json`
files pass `schema_v1` validation via `scripts/replay_schema_check.py`.

**Files changed in 2dbf262:**
- `nova/core/artifact.py` (+shape extraction)
- `nova/core/loop.py` (+enum coercion, NameError fix)
- `nova/core/schemas.py` (+IterationStatus acceptance)
- `pyproject.toml` (−unused deps)
- `tests/test_enrich_artifact_shape.py` (NEW)

**Risk:** None — validation record.

**Recommendation:** Reference `experiments/smoke_step4b_002/` as the regression
baseline when modifying `enrich_artifact` or the Reflector scoring path.

---

## Summary (Updated 2026-05-04)

| # | File | Severity | Blocker? | Action |
|---|------|----------|----------|--------|
| 1 | reflector.py | Low | No | Defer |
| 2 | dream_lab.py | Medium | No (Block D) | Patch when reactivated |
| 3 | loop.py embedder | — | Resolved | Add validator (preventive) |
| 4 | replay_schema_check.py × 2 | Low | No | Documented; do not duplicate basename |
| 5 | per-iteration storage | — | Informational | Treat as load-bearing contract |
| 6 | Step 4b validation | — | Resolved | Use smoke_step4b_002 as regression baseline |
