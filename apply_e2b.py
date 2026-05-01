#!/usr/bin/env python3
"""Atomic patch for E-2b: wire NomicEmbedder into _run_one_iteration."""
import re
from pathlib import Path

path = Path(__file__).parent / "nova/core/loop.py"
src = path.read_text()
original = src

# --- Edit 1: Add import ---
import_anchor = "from nova.core.artifact import"
if "from nova.core.embedder import NomicEmbedder" not in src:
    pattern = re.compile(rf"(^{re.escape(import_anchor)}[^\n]*\n)", re.MULTILINE)
    m = pattern.search(src)
    if not m:
        raise SystemExit("FAIL: could not locate artifact import anchor")
    src = src[:m.end()] + "from nova.core.embedder import NomicEmbedder\n" + src[m.end():]
    print("[1/3] Added NomicEmbedder import")
else:
    print("[1/3] Import already present, skipping")

# --- Edit 2: Update signature ---
old_sig = (
    "def _run_one_iteration(\n"
    "    i: int, hypothesis: str, goal: str, critique: str, cfg: LoopConfig\n"
    ") -> IterationRecord:"
)
new_sig = (
    "def _run_one_iteration(\n"
    "    i: int, hypothesis: str, goal: str, critique: str, cfg: LoopConfig,\n"
    "    embedder: Optional[NomicEmbedder] = None,\n"
    ") -> IterationRecord:"
)
if old_sig not in src:
    raise SystemExit("FAIL: could not find original signature exactly")
src = src.replace(old_sig, new_sig, 1)
print("[2/3] Updated signature")

# --- Edit 3: Insert embedding block after code_hash line ---
hash_line = '    rec.code_hash = hashlib.sha256(rec.code.encode("utf-8")).hexdigest()[:16]\n'
embed_block = (
    "\n"
    "    # --- Embedding (soft-fail; embedder.embed() returns None on failure) ---\n"
    "    if embedder is not None:\n"
    "        try:\n"
    "            rec.embedding = embedder.embed(rec.code)\n"
    "        except Exception as e:\n"
    "            log.warning(\"embedder.embed raised for iter %d: %s\", i, e)\n"
    "            rec.embedding = None\n"
)
if hash_line not in src:
    raise SystemExit("FAIL: could not find code_hash line exactly")
if "rec.embedding = embedder.embed" in src:
    print("[3/3] Embedding block already present, skipping")
else:
    src = src.replace(hash_line, hash_line + embed_block, 1)
    print("[3/3] Inserted embedding block")

if src == original:
    print("No changes made.")
else:
    path.write_text(src)
    print(f"\nWrote {len(src)} bytes to {path}")
