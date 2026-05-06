# Educational Brief: Track B SHA-256 Provenance

## What We Built

We added **tamper-evident provenance** to Nova's embedding artifacts. In plain terms: every stored vector now carries a cryptographic receipt proving which source text produced it.

### The core idea

When Nova embeds a piece of text, three things get stored together:

1. The **vector** (the model's output — a list of floats representing meaning)
2. The **source text** (the input the model saw)
3. A **SHA-256 hash** of that source text (a 64-character fingerprint)

Later — weeks, months, after migrations, after edits, after bugs — anyone can re-hash the stored source text and compare it to the stored fingerprint. Match means the record is intact. Mismatch means *something changed* between when the vector was computed and now.

### Why this matters

Without provenance, an embedding is an orphan. You have a vector, you have some text next to it, and you have *faith* that they correspond. Faith doesn't survive a year of migrations, schema changes, and well-meaning cleanup scripts. SHA-256 replaces faith with arithmetic.

## The Three Decisions That Define Track B

### 1. Hash post-truncation, not pre-truncation

The embedder truncates text to 2000 characters before feeding it to the model. We hash *after* truncation — the hash witnesses what the model actually saw, not what we wished it had seen.

**Why this is subtle:** It feels more "honest" to hash the original input. But the vector is a function of the truncated input, so binding the hash to anything else creates a permanent mismatch between the vector's true input and the hash's claimed input. The hash must witness reality, not intention.

### 2. Schema version is *derived*, not *declared*

A record has `source_sha256` → it's v2. No hash → it's v1. The writer doesn't get to label its own output; the schema reads the contents and decides.

**Why this matters:** Self-declared versions are lies waiting to happen. A bug could write a v2 record without a hash and call it v2. With derivation, that record is *structurally impossible* — Pydantic rejects it at validation time. The invariant is enforced by the type system, not by discipline.

### 3. Verification never raises

`verify_embedding()` returns `"ok"`, `"mismatch"`, or `"skipped"`. It never throws. A replay tool can scan 10,000 records and report comprehensively, even if 47 of them are corrupt.

**Why this matters:** Exceptions are control flow. Diagnostics are data. Confusing the two means your tooling aborts on the first problem instead of giving you a complete picture. Track B treats integrity violations as findings to report, not emergencies to halt on.

## What's Locked Now

- 29 tests, 0.14 seconds, covering every invariant
- Schema rejects malformed records at construction time
- Replay tool (`tools/replay_schema_check.py`) walks files or directories with JSON output for CI
- ADR-137 captures the *why* — including the rejected alternatives, so future-you doesn't reopen settled questions

## Where We're Headed

### Track C: Model Provenance (the obvious next gap)

Track B proves the *input* is intact. It says nothing about which *model* produced the vector. If we upgrade from `nomic-embed-text-v1` to `v1.5`, every existing vector becomes ambiguous — same source, different model, no way to tell which.

Track C would add fields like `model_name`, `model_version`, and possibly a hash of the model weights. Then a vector becomes fully attributable: "this float array came from *this* text through *this* model."

Open questions for Track C scoping:
- Do we hash the model itself, or trust version strings? (Hashing is rigorous but expensive; strings are cheap but spoofable.)
- How do we handle model upgrades — re-embed everything, or accept multi-model corpora?
- Does model provenance go in the artifact, or in a separate manifest?

### The v1 Migration Question (deferred but looming)

Right now Nova has a mix of v1 (pre-Track-B) and v2 records. The `--require-v2` flag is deferred until we decide:

- **Option A:** Re-embed all v1 records to give them v2 provenance
- **Option B:** Accept v1 records as permanently legacy, age them out naturally
- **Option C:** Hybrid — re-embed records that are still actively retrieved, let cold ones expire

Each has cost/benefit tradeoffs around compute, retrieval consistency, and how aggressively we want to enforce v2 in tooling.

### Phase 10 Beyond Step 4b

Step 4b was about *trustworthy storage*. The remaining steps in Phase 10 build the imagination engine on top of that storage. Now that we trust the substrate, we can build on it without anxiety about what we're standing on.

## The Meta-Lesson

Track B is small — a hash function, a few validators, a tool. But it demonstrates a pattern worth naming:

> **Make correctness structural, not behavioral.**

The schema doesn't *check* that v2 records have hashes — it makes "v2 record without hash" inexpressible. The verifier doesn't *decide* whether to halt on mismatch — it returns data and lets callers decide. The hash doesn't *describe* the input — it witnesses it.

Each of these moves correctness from "we remembered to do the right thing" to "the wrong thing cannot be done." That's the difference between a system that's correct because we're careful and a system that's correct because it can't be otherwise.

That's the standard worth holding for everything Phase 10 builds next.

---

Ready to come back to it whenever. Want me to hold this brief somewhere in the repo (e.g., `docs/briefs/`) or is it just for the break?