# 🌀 Dazchicago | Project Nova (Imagination Engine)

# Nova — The Imagination Engine

**A Local-First Sovereign Intelligence Lattice**

> Project Nova is a local-first, sovereign AI architecture developed by
> **Dazchicago**. It is unaffiliated with any cloud-model provider.
> Nova is not an assistant. Nova is an **Imagination Engine**.

---

## What Is the Imagination Engine?

Most AI systems are reactive: you prompt, they answer. Nova inverts that
relationship.

The **Imagination Engine** is a closed-loop architecture in which one model
*dreams* (generates candidate ideas, code, or artifacts), a second model
*reflects* (scores and explains), and an embedding layer remembers
*shapes* — the recurring conceptual patterns that emerge across every dream.

Over time, Nova doesn't just answer questions. She develops a **resonant
memory** of her own thinking, recognizes when new ideas echo old ones, and
uses that recognition to imagine further.

This is the engine. The mission is what we point it at.

---

## Architecture Overview

Nova runs as a **two-host, three-role** system on local hardware. No cloud
APIs. No telemetry. No vendor lock-in.

### Hosts

| Host | Hardware | Role |
|------|----------|------|
| **Dreamer Host** | Windows · RTX 5090 · LM Studio (port 1234) | Generation |
| **Orchestrator Host** | MacBook Pro · Ollama · local storage | Reflection, embeddings, control plane |

Communication runs over standard LAN (`10.0.0.195` ↔ `10.0.0.167`).

### Roles (AD-003)

1. **The Dreamer** — `llama-3.1-nemotron-70b-instruct-hf`
   Generates candidate outputs. Lives on the GPU host.
2. **The Reflector** — `phi4:latest`
   Scores outputs and, in Tutor Mode, explains *why* a score was given.
3. **The Embedder** — `nomic-embed-text` (768-dim)
   Produces shape vectors for resonance scoring. Mac-only (AD-004).

---

## Key Subsystems

### 1. Nova Output Engine (NOE)
The core **Judge-and-Improve loop**. The Dreamer generates; the Reflector
scores. If the score falls below threshold, the loop regenerates until
quality is reached or a budget is exhausted.

### 2. Tutor Mode *(Block E — complete)*
The Reflector operates in a **two-step score-then-explain** pattern
(AD-006, AD-007). Each reflection produces structured feedback appended
to `docs/learning_log.md`. Every cycle becomes a teaching moment — for
Nova, and for the human watching her think.

### 3. Shape Resonance *(Phase 9 / Block D — in progress)*
Every artifact Nova produces — dreams, reflections, outputs — is embedded
into a 768-dimensional vector and persisted under `~/nova/data/shapes/`.
Cosine similarity surfaces **resonance**: the moment a new idea echoes an
old one. This is the substrate for long-term memory and recurring-theme
detection.

### 4. Lab Zero *(planned)*
A hardened sandbox in which Nova forms hypotheses, writes experimental
Python, executes it under strict isolation, and reflects on the results.
Lab Zero turns the Imagination Engine from passive generator into
**autonomous explorer**.

### 5. AST Safety Shield *(planned)*
Compiler-grade security. Before any code Nova writes is executed, it is
parsed into an Abstract Syntax Tree and scanned for forbidden operations
(filesystem escape, network calls, subprocess spawning, etc.). The
sovereign host stays sovereign.

---

## Architectural Decisions (Locked)

| ID | Decision |
|----|----------|
| AD-001 | Local-only execution; no cloud APIs |
| AD-002 | Two-host split (Windows Dreamer / Mac Orchestrator) |
| AD-003 | Three-role split (Dreamer / Reflector / Embedder) |
| AD-004 | Embeddings run on Mac only |
| AD-005 | Dreamer model swap revisit at Phase 10 |
| AD-006 | Reflector operates in Tutor Mode |
| AD-007 | Tutor Mode uses two-step score-then-explain |
| AD-008 | Mandatory venv for dependency isolation |

Full rationale lives in [`docs/decisions.md`](docs/decisions.md).

---

## Current Status

- **Project version:** 0.8.4 · **API version:** 0.11.0
- **Phases 7, 8, 8.5:** complete
- **Block E (Tutor Mode):** complete
- **Block D (Shape Extraction & Resonance):** in progress
- **Test suite:** 117 passing
- **Next milestone:** Phase 10 — Dreamer model re-evaluation, Lab Zero
  groundwork

---

## The Mission

To transform AI from a reactive assistant into an **autonomous explorer**
that runs entirely on hardware its operator owns.

Nova exists to:

- **Operate Locally** — run on user-owned hardware, free of cloud
  dependencies and surveillance.
- **Remain Sovereign** — no external kill-switches, no forced updates,
  no vendor leverage.
- **Learn & Evolve** — improve through local reflection, resonance
  memory, and autonomous experimentation in Lab Zero.
- **Stay Safe** — protect the host through layered defenses (AST shield,
  venv isolation, local-only networking).
- **Be Transparent** — open-source, auditable, and reproducible.

The long-term goal is not a smarter chatbot. It is a private, durable,
**personally-owned thinking partner** — one that imagines, remembers,
and grows alongside the person who built it.

---

## Repository

This project lives at **github.com/dazchicago/nova** (the Imagination
Engine).

## Getting Started

*Setup documentation is a Phase 10 deliverable. The system currently
requires a Windows host with LM Studio + Nemotron 70B and a Mac host
with Ollama + phi4 + nomic-embed-text on the same LAN.*

## Contributing

*Contribution guidelines forthcoming. The project is intentionally
small-team during foundation phases.*

## License

GPL-3.0 — see [LICENSE](LICENSE).

---

*Built by dazchicago. Urban logic, and pure grit, Local-first. Sovereign by design.*
