
---

# `nova/migration/README.md`

## Why this directory exists

This is quarantine. Everything in here exists to drag v0 records forward to v1 and nothing else. When the last v0 record is gone, this directory gets deleted. Plan accordingly.

## Why the discriminator lives here, not in `core/`

`detect_v0_kind()` infers what a record *is* by looking at its shape. That's a v0 problem. v1 records carry `record_kind` as an explicit field — no guessing required.

We deliberately did **not** promote the heuristic into `core/provenance.py`. Two reasons:

1. **It would be a permanent pin against deletion.** Anything in `core/` is load-bearing forever. Anything in `migration/` has an expiration date.
2. **It would invite misuse.** A future contributor would see a general-purpose `detect_kind()` and reach for it instead of just reading `record_kind` off a v1 record. Now we have two code paths that can disagree, and disagreement in provenance code is how you lose a corpus.

The v1 accessor is `core/provenance.record_kind()`. It's three lines and it fails loud. Use that.

## How the heuristic decides

- **v0 iteration** → has `iteration` (int) *and* `dreamer_duration_s`
- **v0 summary** → has `experiment_id` *and* `scores` (list)

These keys were picked because they show up in 100% of the v0 corpus we surveyed and they don't overlap. Don't loosen these conditions without re-surveying. If the heuristic ever gets fuzzy, the migration gets fuzzy, and bad records ship downstream.

## What happens if you hand it a v1 record

It raises. On purpose. v1 records have no business in this code path — they go through `record_kind()`. Keeping the boundary sharp here keeps the boundary sharp everywhere.

## When does this directory get deleted

When v0 is no longer a supported input anywhere in the deployment. Current policy: v0 is "legacy, migrate on read." Targeted removal is post-v3. Track it against the schema deprecation policy, not against vibes.

## Fixture notes

Golden fixtures under `tests/fixtures/v0/` are pulled from the 2026-04-27 CLT iteration and the `smoke_1777263238` summary. Only timestamps are normalized. The F-002 matplotlib cache noise in `sandbox_stderr` is preserved on purpose — that's evidence, not dirt. Don't clean it.

---
