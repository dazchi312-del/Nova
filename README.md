# Nova — The Imagination Engine

> A local-first, sovereign AI operating system.
> Urban logic meets pure grit. DIY or die.

![License](https://img.shields.io/badge/license-GPL--3.0-blue)
![Status](https://img.shields.io/badge/status-active%20research-orange)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

---

## What Nova Is

Nova is a two-machine local AI system designed to run, reason, and remember
without depending on cloud APIs. It is built around the idea that a personal
intelligence should be **owned, inspectable, and reproducible** — not rented.

Most AI tools are reactive: you prompt, they answer. Nova is structured as a
closed loop: one model generates, a second model reflects, and a provenance
layer records every artifact with a content hash so that nothing the system
produces is unverifiable later.

This repository contains the working code, schemas, tests, and operational
tools for that system.

## Architecture

Nova runs across two machines connected over a local network:

- **Dreamer** — generation host (RTX 5090, Qwen 2.5 32B). Produces candidate
  outputs.
- **Orchestrator** — reflection and control host (Apple Silicon, Phi-4).
  Scores, critiques, and routes.

Artifacts produced by either machine are recorded in a local store with
SHA-256 content hashes and schema-versioned metadata. Migration tooling
exists for evolving the schema without losing historical records.

┌─────────────┐ ┌──────────────────┐ │ Dreamer │ ──────▶ │ Orchestrator │ │ (generate) │ │ (reflect) │ └─────────────┘ └──────────────────┘ │ │ └──────────┬─────────────┘ ▼ ┌─────────────────┐ │ Provenance │ │ (SHA-256 + │ │ schema v1) │ └─────────────────┘


## Current Status

This is an **active research project**, not a finished product. Subsystems
land in phases; each phase closes when its tests pass and its artifacts are
reproducible.

### Working today

- Dual-machine generation/reflection loop
- SHA-256 content addressing for all artifacts (Track B — closed)
- Schema-versioned record store with migration tooling
- Test suite covering provenance, replay, and schema validation
- Provenance inspection CLI (`tools/`)

### In progress

- Track C: `model_record.json` schema and registry
- Phase 11: capability expansion (see `docs/briefs/`)

### Phase log

Detailed phase-by-phase logs live in `docs/` and `logs/`. Tags mark
checkpoint releases (`v0.7.0`, `v0.8.3`, `v0.9.0`).

## Repository Layout

| Path | Purpose |
|------|---------|
| `nova/` | Core package — generation, reflection, provenance |
| `tests/` | pytest suite |
| `tools/` | Operational CLIs (inspection, migration) |
| `docs/` | Design briefs, architecture notes |
| `experiments/` | Throwaway probes and validation runs |
| `scripts/` | Build and ops scripts |
| `db/`, `nova_data/` | Local stores (gitignored where appropriate) |
| `docker/` | Container definitions for reproducible runs |

## Requirements

- Python 3.11+
- A GPU host capable of running a 32B-parameter model (Dreamer)
- A second host for orchestration (any modern Mac or Linux box)
- Local network connectivity between the two

Exact model choices are configurable; the defaults assume Qwen 2.5 32B on
the Dreamer and Phi-4 on the Orchestrator.

## Getting Started

> Nova is not yet packaged for one-command install. The steps below assume
> you are comfortable with Python environments and local networking.

```bash
git clone https://github.com/dazchi312-del/Nova-Imagination-Engine.git
cd Nova-Imagination-Engine
pip install -e ".[dev]"
pytest

## Licensing
- **Code:** AGPL-3.0 (`LICENSE-CODE`)
- **Documentation:** CC BY 4.0 (`LICENSE-DOCS`)
- **Schemas:** MIT (`LICENSE-SCHEMAS`)
- **Brand:** "Nova," the seal, and "Dazchicago" are trademarks of the
  project author. See `TRADEMARKS.md`.

