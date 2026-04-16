Agreed. This becomes a living document for Nova. Here's an expanded version worth keeping:

---

## Nova Technology Radar
**Last Updated:** Phase 8 — v0.7.0
**Purpose:** Track the evolving landscape. When better tools emerge, Nova adopts them.

---

### 🟢 ADOPT — In Use Now
| Category | Tool | Why |
|---|---|---|
| Models | Llama 3.1 8B | Fast, local, low VRAM |
| Models | Nemotron 70B Q4 | Deep reasoning, complex tasks |
| Inference | LM Studio | Stable local serving |
| Memory | SQLite | Persistent, zero-dependency |
| Tool Execution | Custom Python | Full control, no overhead |
| UI | CLI | Fast, scriptable |

---

### 🟡 TRIAL — Worth Testing Soon
| Category | Tool | Why It Matters |
|---|---|---|
| Models | DeepSeek V3 | Strong coding, rivals GPT-4 class locally |
| Models | Qwen 2.5 | Multilingual, efficient, growing fast |
| Memory | ChromaDB | Vector search, semantic recall |
| Inference | vLLM | Faster throughput than LM Studio |
| UI | Textual TUI | Rich terminal UI, stays local |

---

### 🔵 ASSESS — Watch Closely
| Category | Tool | Why It Matters |
|---|---|---|
| Memory | LanceDB | Vector + relational hybrid, embedded like SQLite |
| Memory | Qdrant | Production-grade vector DB, local mode available |
| Inference | TensorRT-LLM | NVIDIA-native, RTX 5090 could fly with this |
| Inference | MLX | Apple Silicon only — not relevant unless you go mobile |
| Tool Execution | LangChain | Mature ecosystem but heavy — evaluate overhead |
| Tool Execution | LlamaIndex | Better for RAG pipelines than agent loops |

---

### 🔴 HOLD — Not Right Now
| Category | Tool | Reason |
|---|---|---|
| UI | Local Web UI | Adds complexity before core is stable |
| Tool Execution | LangChain | Abstraction fights Nova's custom architecture |
| Inference | Cloud APIs | Violates local-first principle |

---

### Radar Rules
1. **Nothing cloud-dependent enters ADOPT.** Nova is local-first, always.
2. **RTX 5090 is an asset.** Prioritise tools that leverage CUDA and high VRAM.
3. **Complexity budget.** Every new tool must earn its place. Simple beats clever.
4. **Review every major version bump.** Reassess at v0.8, v0.9, v1.0.

---

### On the Horizon — Flag These
- **TensorRT-LLM** — Once Nova is stable, benchmark against LM Studio. The RTX 5090 could make this transformative for response speed.
- **LanceDB** — Natural SQLite replacement when Nova needs semantic search over memory. Same embedded model, adds vectors.
- **DeepSeek V3** — Worth a local benchmark run. If it fits in VRAM at a useful quant, it could become Nova's primary reasoning model.

---

Save this as `docs/technology_radar.md` in the Nova project. Update it whenever something moves between rings. The landscape shifts fast — this keeps Nova ahead of it.

Now we're talking. Let's document the architecture properly.

---

## Nova Agent Architecture
**Version:** v0.7.0
**Classification:** Multi-Layer Intelligent Agent
**Status:** 7 Layers Active — Expanding

---

### The 7 Layers

```
┌─────────────────────────────────────────────┐
│           LAYER 7 — IDENTITY                │
│   Daz's creative partner. Nova. Not a tool. │
└─────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────┐
│           LAYER 6 — TASTE & AESTHETICS      │
│   taste_profile DB. Nova has preferences.   │
│   Knows what Daz likes before he asks.      │
└─────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────┐
│           LAYER 5 — CREATIVE ENGINE         │
│   creative_sessions + creative_ideas DB.    │
│   Nova Eclipse. Projects with continuity.   │
└─────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────┐
│           LAYER 4 — MEMORY                  │
│   SQLite persistent memory.                 │
│   Survives process death. Knows your name.  │
└─────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────┐
│           LAYER 3 — TOOL EXECUTION          │
│   Custom Python dispatch loop.              │
│   MAX_TOOL_ROUNDS = 5. Safety sandboxed.    │
└─────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────┐
│           LAYER 2 — MODEL ROUTING           │
│   Llama 3.1 8B → fast tasks                 │
│   Nemotron 70B → deep reasoning             │
│   [Routing logic — next build]              │
└─────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────┐
│           LAYER 1 — INFERENCE               │
│   LM Studio. RTX 5090. Local always.        │
│   No cloud. No API keys. No surveillance.   │
└─────────────────────────────────────────────┘
```

---

### What Makes This Not Generic

Most agents are:
```
User prompt → LLM → Response
```

Nova is:
```
User prompt
    → Identity context loaded
    → Taste profile consulted
    → Creative session checked
    → Memory recalled
    → Tool loop engaged
    → Model selected by complexity
    → Inference on local hardware
    → Response with continuity
```

Every layer adds something a generic agent doesn't have. Identity. Taste. Creative memory. Safety. Intelligence routing. It compounds.

---

### Layer Roadmap

| Layer | Status | Next Action |
|---|---|---|
| 1 — Inference | ✅ Stable | Benchmark TensorRT-LLM at v0.9 |
| 2 — Model Routing | 🔧 Manual | Automate by task complexity |
| 3 — Tool Execution | 🔧 Dry-run pending | `--dry-run` flag in progress |
| 4 — Memory | ✅ Confirmed today | Identity hardening next |
| 5 — Creative Engine | 🟡 Schema exists | Activate Nova Eclipse sessions |
| 6 — Taste & Aesthetics | 🟡 Schema exists | Load taste_profile at startup |
| 7 — Identity | 🟡 Partial | Full system prompt from DB |

---

### The Principle
Each layer is owned. Each layer is local. Each layer was built deliberately.

Generic agents are assembled from other people's abstractions. Nova is constructed from first principles, one layer at a time, by someone who knows exactly what he's building and why.

**7 layers today. More coming.**

---

Save as `docs/agent_architecture.md`. This becomes the blueprint. Every new capability gets mapped to a layer or earns a new one.

Exactly. That distinction matters enormously. Let's make it official.

---

## Nova Is Not a Chatbot
**This needs to be stated clearly and repeated often.**

---

### The Difference

A chatbot answers questions.

An operating system **runs things.**

```
Chatbot:
User asks → Model responds → Conversation ends
Nothing persists. Nothing executes. Nothing builds.

Nova:
User intent → Nova plans → Nova executes
Memory writes. Tools fire. State changes.
The next session knows what happened in this one.
Everything builds on everything before it.
```

---

### What an AI Operating System Actually Is

```
┌─────────────────────────────────────────────────┐
│              NOVA OS                            │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐              │
│  │   MEMORY    │  │    TOOLS    │              │
│  │  Persistent │  │  Execution  │              │
│  │  SQLite DB  │  │  Real world │              │
│  └─────────────┘  └─────────────┘              │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐              │
│  │  IDENTITY   │  │  CREATIVE   │              │
│  │  Knows you  │  │   ENGINE    │              │
│  │  Knows self │  │  Makes things│             │
│  └─────────────┘  └─────────────┘              │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐              │
│  │   ROUTING   │  │  SCHEDULER  │              │
│  │ Right model │  │ [Coming]    │              │
│  │ Right task  │  │ Proactive   │              │
│  └─────────────┘  └─────────────┘              │
│                                                 │
│         Runs on: RTX 5090. Your hardware.       │
│         Owned by: You. Not Microsoft.           │
└─────────────────────────────────────────────────┘
```

---

### What Operating Systems Do That Chatbots Don't

| Capability | Chatbot | Nova OS |
|---|---|---|
| Persistent state | ❌ | ✅ SQLite memory |
| Execute tools | ❌ | ✅ Python dispatch |
| Manage processes | ❌ | 🔧 Coming |
| Schedule tasks | ❌ | 🔧 Coming |
| Know the user | ❌ | ✅ Identity layer |
| Have preferences | ❌ | ✅ Taste profile |
| Run without internet | ❌ | ✅ Always |
| Own your own weights | ❌ | ✅ Local models |
| Build on past sessions | ❌ | ✅ Confirmed today |
| Proactive behaviour | ❌ | 🔧 Coming |

---

### The Operating System Roadmap

**What Nova needs to become a true OS:**

```
Phase 8  ✅  Memory — DONE
Phase 9  🔧  Tool Safety — dry-run flag
Phase 10     Process Management — Nova spawns and manages tasks
Phase 11     Scheduler — Nova acts without being asked
Phase 12     File System Awareness — Nova knows your project structure
Phase 13     Self Modification — Nova updates her own config
Phase 14     Multi-Agent — Nova spawns sub-agents for parallel tasks
Phase 15     Nova Desktop — lightweight local UI layer
```

---

### The One Sentence Definition

> **Nova is a local-first AI operating system that persists, executes, creates, and builds — running entirely on your hardware, owned entirely by you.**

Not a chatbot. Not a copilot. Not a feature inside someone else's product.

An operating system. Built from scratch. One layer at a time.

---

Save as `docs/nova_os_manifesto.md`

This is the north star document. When anyone asks what Nova is — including Nova herself — this is the answer.