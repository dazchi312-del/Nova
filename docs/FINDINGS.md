# Nova Imagination Engine — Findings Register

**Purpose**: This document records empirical findings discovered during
corpus analysis, migration work, and operational use of the Nova
Imagination Engine. Each finding is assigned a stable identifier (F-NNN),
characterized with evidence, and tracked through to mitigation.

**Audience**: Maintainers, contributors, and downstream consumers of
v0 → v1 migrated records.

**Conventions**:
- Findings are append-only. Once an F-ID is assigned, it is never reused
  or renumbered, even if the finding is later invalidated (mark as
  `Status: Withdrawn` instead).
- Severity levels: `Critical` (blocks correctness), `High` (data integrity
  or security), `Medium` (operational hygiene), `Low` (cosmetic / minor).
- Each finding states its mitigation status explicitly. Open findings
  must have a tracking issue or a documented reason for deferral.

---

## Index

| ID    | Title                                              | Severity | Status                  |
|-------|----------------------------------------------------|----------|-------------------------|
| F-001 | v0 Lean Scorer is Binary, Not Continuous           | High     | Documented; Mitigated   |
| F-002 | Matplotlib Font Cache Leak in Sandbox Artifacts    | Medium   | Documented; Mitigated   |

---

## F-001: v0 Lean Scorer is Binary, Not Continuous

**Severity**: High (data integrity)
**Status**: Documented; mitigated in migration
**Affects**: All Shape B (lean iteration) and Shape C (lean experiment) records
**Discovered**: Phase 10 Step 4b corpus analysis
**Reporter**: Migration audit pass

### Summary

The v0 lean scoring path produced exactly two values across the entire
analyzed corpus: `0.0` and `0.85`. Despite presenting as a float in the
nominal range `[0.0, 1.0]`, it functioned as a binary pass/fail
classifier. Intermediate scores reported in `score_progression` arrays
are therefore **not interpretable as quality gradients** and must not
be compared, averaged, or otherwise aggregated as if they were.

### Evidence

**E-001.1 — Corpus-wide score distribution**

