"""
tools/replay_schema_check.py

Batch verification tool for embedding artifact records.

Walks a file or directory of JSON records, validates each against the
EmbeddingArtifact schema, and runs verify_embedding() on v2 records to
confirm the source_sha256 still matches the captured source_text.

Exit codes:
    0  all records ok or skipped (v1, no hash)
    1  one or more mismatches or invalid records
    2  usage error (path does not exist, etc.)

Usage:
    python -m tools.replay_schema_check artifacts/
    python -m tools.replay_schema_check path/to/record.json
    python -m tools.replay_schema_check artifacts/ --json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from nova.core.provenance import verify_embedding
from nova.core.schemas.artifact import EmbeddingArtifact


@dataclass
class RecordResult:
    path: str
    status: str  # "ok" | "skipped" | "mismatch" | "invalid"
    schema_version: int | None
    dim: int | None
    detail: str  # human-readable note (error message, "no source_sha256", etc.)


def check_record(path: Path) -> RecordResult:
    """Load, validate, and verify a single JSON record. Never raises."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        return RecordResult(str(path), "invalid", None, None, f"read error: {e}")

    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError as e:
        return RecordResult(str(path), "invalid", None, None, f"json decode error: {e}")

    try:
        artifact = EmbeddingArtifact.model_validate(data)
    except ValidationError as e:
        # Compact the validation error to a single line for table output
        first_err = e.errors()[0] if e.errors() else {}
        loc = ".".join(str(x) for x in first_err.get("loc", []))
        msg = first_err.get("msg", str(e))
        return RecordResult(
            str(path), "invalid", None, None, f"schema error at {loc}: {msg}"
        )

    schema_version = artifact.schema_version
    dim = artifact.metadata.dim

    status = verify_embedding(artifact)

    if status == "skipped":
        detail = "v1 record (no source_sha256)"
    elif status == "ok":
        detail = ""
    elif status == "mismatch":
        detail = "source_sha256 does not match source_text"
    else:
        detail = f"unknown verify status: {status}"

    return RecordResult(str(path), status, schema_version, dim, detail)


def collect_paths(target: Path) -> list[Path]:
    """Resolve target to a sorted list of JSON file paths."""
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(target.rglob("*.json"))
    return []


def render_human(results: list[RecordResult]) -> str:
    """Tab-aligned table for terminal output."""
    if not results:
        return "No records found.\n"

    lines: list[str] = []
    for r in results:
        sv = f"v{r.schema_version}" if r.schema_version is not None else "-"
        dim = f"{r.dim} dims" if r.dim is not None else "-"
        status_label = r.status.upper() if r.status in ("invalid", "mismatch") else r.status
        suffix = f"  ({r.detail})" if r.detail else ""
        lines.append(f"{r.path}\t{status_label}\t{sv}\t{dim}{suffix}")

    counts = summarize(results)
    summary = (
        f"\nSummary: {counts['ok']} ok, {counts['skipped']} skipped, "
        f"{counts['mismatch']} mismatch, {counts['invalid']} invalid"
    )
    lines.append(summary)
    return "\n".join(lines) + "\n"


def render_json(results: list[RecordResult]) -> str:
    """Machine-readable output for CI."""
    payload = {
        "summary": summarize(results),
        "records": [asdict(r) for r in results],
    }
    return json.dumps(payload, indent=2) + "\n"


def summarize(results: list[RecordResult]) -> dict[str, int]:
    counts = {"ok": 0, "skipped": 0, "mismatch": 0, "invalid": 0, "total": len(results)}
    for r in results:
        if r.status in counts:
            counts[r.status] += 1
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="replay_schema_check",
        description="Validate and verify embedding artifact records.",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to a JSON record or a directory of records (recursive).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output for CI consumption.",
    )
    args = parser.parse_args(argv)

    target: Path = args.path
    if not target.exists():
        print(f"error: path does not exist: {target}", file=sys.stderr)
        return 2

    paths = collect_paths(target)
    results = [check_record(p) for p in paths]

    output = render_json(results) if args.json else render_human(results)
    sys.stdout.write(output)

    counts = summarize(results)
    if counts["mismatch"] > 0 or counts["invalid"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
