# Project Nova — Environment Reference

**Last verified:** Session 37, [DATE]
**API version:** v0.11.0
**Project version:** v0.8.4

---

## Topology (per AD-002: Two-Host Split)


- **Mac** runs: orchestration loop, Curator, Reflector, embeddings, storage
- **Windows** runs: Dreamer (vision-language generation)

---

## Canonical Model Strings

| Role        | Model                          | Host    | Endpoint                          |
|-------------|--------------------------------|---------|-----------------------------------|
| Dreamer     | `qwen2.5-vl-32b-instruct`      | Windows | `http://10.0.0.195:1234/v1`       |
| Curator     | `phi4:latest`                  | Mac     | `http://localhost:11434`          |
| Reflector   | `phi4:latest`                  | Mac     | `http://localhost:11434`          |
| Embeddings  | `nomic-embed-text:latest`      | Mac     | `http://localhost:11434`          |

These strings are authoritative. Any drift in `loop.py` or config from these values is a bug.

---

## Service Details

### Mac — Ollama
- Port: `11434`
- API style: native Ollama (`/api/generate`, `/api/embeddings`) and OpenAI-compat (`/v1/...`)
- Models present: `phi4:latest`, `nomic-embed-text:latest`

### Windows — LM Studio
- Port: `1234`
- API style: OpenAI-compatible (`/v1/...`)
- Bound to `0.0.0.0` (LAN-accessible)
- Firewall rule required: inbound TCP 1234 allowed
- Loaded models: `qwen2.5-vl-32b-instruct`, `text-embedding-nomic-embed-text-v1.5`

---

## Important Notes

### AD-004: Embeddings are Mac-only
LM Studio on Windows also exposes `text-embedding-nomic-embed-text-v1.5`.
**Do not use it.** All embedding calls go through Mac Ollama.
Rationale: keep embedding pipeline co-located with storage/orchestration; avoid cross-host latency on high-frequency calls.

### TD-002: Phi-4 instruction-following drift
During Session 37 smoke test, Phi-4 returned `"Alive."` when asked to reply with exactly `"alive"`.
Mitigation in Curator/Reflector prompts:
- Use JSON mode / structured output where the API supports it
- Add explicit "no punctuation, no capitalization, no commentary" guards
- Strip and normalize Phi-4 output before parsing

### TD-003: Dreamer model selection unresolved
Current Dreamer is `qwen2.5-vl-32b-instruct`. Per AD-005, Dreamer swap occurs at Phase 10.
Revisit quantization and alternative VL models before Phase 10 entry.

---

## Smoke Test Procedure

To re-verify environment health at the start of any session:

```bash
# Mac Ollama up?
curl http://localhost:11434/api/tags

# Mac Phi-4 generation
curl http://localhost:11434/api/generate -d '{"model":"phi4:latest","prompt":"Reply with exactly: alive","stream":false}'

# Mac embeddings
curl http://localhost:11434/api/embeddings -d '{"model":"nomic-embed-text:latest","prompt":"test"}'

# Windows Dreamer reachable?
curl http://10.0.0.195:1234/v1/models

# Windows Dreamer generation
curl http://10.0.0.195:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5-vl-32b-instruct","messages":[{"role":"user","content":"Reply with exactly: ok"}],"max_tokens":10,"temperature":0}'

---

**Your move:**

1. Save that to `docs/environment.md` (fill in `[DATE]`)
2. Manually edit anything you want to phrase differently (per your educational/manual-edits directive)
3. `git add docs/environment.md && git commit -m "docs: A.6 environment reference, Session 37"`

When committed, **Block A is closed**.

---

**To start Block C (loop.py refactor), paste:**

1. Current contents of `loop.py`
2. Current contents of your config file (whichever holds model strings now — `config.py`, `.env`, `settings.py`, etc.)

I'll do a structural read first, then we plan the refactor before any code changes.
