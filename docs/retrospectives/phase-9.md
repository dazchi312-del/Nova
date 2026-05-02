# Phase 9 Retrospective — Shape Extraction & Embedding Integration

**Tag:** `phase-9-complete` (commit `5b80d84`)
**Closed:** Block D — Loop Integration
**Follow-up:** `857dcba` (Path B hygiene pass)

---

## What Phase 9 delivered

- End-to-end embedding pipeline: artifact → `EmbeddingMetadata` → persisted record.
- 768-dim vectors via `nomic-embed-text` on the Orchestrator (192.168.100.2).
- Verified persistence schema: `vector`, `model`, `dim`, `source_text`, `model_blob_sha`.
- Smoke test `blockd_smoke_002` passes with score = 1.00, 478.8ms baseline latency on M4 Pro.
- `nova` console script wired via `[project.scripts]`.

## What broke, and why

| # | Bug | Root cause | Cost |
|---|---|---|---|
| 1 | URL double-suffix | Config layer appended `/v1` to a URL that already had it | Silent 404s |
| 2 | Reflector 404 | Hardcoded model name not present on Orchestrator | Forced pivot to phi4 shim |
| 3 | Legacy 10.0.0.x IPs | `dream_lab.py`/`reflector.py` predate the 192.168.100.x lattice | Logged as debt; modules dormant |
| 4 | Missing `Any` import | Refactor moved type usage without updating imports | NameError at runtime |
| 5 | Type confusion / double-wrap | `EmbeddingMetadata` silently wrapped twice at persistence boundary | Schema drift, hard to detect |
| 6 | CLI entry point | `if __name__ == "__main__":` indented inside a function after refactor | `python -m nova.core.loop` failed |

## Lessons that became rules

### Fail loud, fail early
Silent URL/config mutation cost the most debugging time. Validation at the
boundary (URL construction, model resolution) must raise, not coerce.

### Two-Phase Rule
Before deleting code that *looks* unused, grep the full tree for usage.
`hashlib` (loop.py:525) and `EmbeddingMetadata` (loop.py:118) both looked
dead at a glance and were load-bearing.

### Raw honest narrative in git
Failed experiment `blockd_smoke_001` was kept in the repository rather than
rewritten out. Future retrospectives can see the actual shape of the work.

### Persistence boundaries need validators
Bug 5 (double-wrap) would have been caught instantly by a Pydantic model
or dataclass `__post_init__` check at the write site. This is the headline
candidate for Block C.

## Deferred items

- **Bug 3:** Patch legacy IPs in `dream_lab.py` and `reflector.py` when those
  modules reactivate. No value in touching dormant code.
- **SHA-256 of `source_text`:** Defer until persisted storage exceeds 100MB.
  Premature now.

## What Phase 9 changes about how we work

1. CLI entry points use the extract-`main()` + module-level guard pattern.
2. Console scripts go through `[project.scripts]`, not `python -m`, for
   user-facing invocation.
3. Setuptools package discovery is explicit (`[tool.setuptools.packages.find]`)
   to keep `experiments/`, `labs/`, `data/` etc. out of the wheel.
4. Type confusion at persistence boundaries is treated as a class of bug,
   not a one-off.

## Block C scoping inputs

- **Headline candidate:** Pydantic/dataclass validators at the persistence
  boundary (writes to `experiments/*/iter*_record.json`).
- **Secondary:** Config validation layer (URL construction, model resolution)
  that raises on ambiguity.
- **Tertiary:** Reactivate `dream_lab.py` with corrected IPs if Block C
  needs the module.
