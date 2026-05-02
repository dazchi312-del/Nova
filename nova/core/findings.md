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
