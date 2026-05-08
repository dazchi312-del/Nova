"""Schema migration: pure functions for lifting v0 records to v1."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable

from nova.schema.constants import (
    CURRENT_SCHEMA_VERSION,
    LEGACY_SCHEMA_VERSION,
    SCHEMA_STATUS_MIGRATED,
)


class MigrationOutcome(Enum):
    """Result of attempting to migrate a single record."""
    ALREADY_CURRENT = "already_current"
    MIGRATED = "migrated"
    UNMIGRATABLE = "unmigratable"


@dataclass(frozen=True)
class MigrationReport:
    """Summary of a migrate_all run."""
    total: int
    already_current: int
    migrated: int
    unmigratable: int
    dry_run: bool

    @property
    def changed(self) -> int:
        return self.migrated


def _compute_legacy_sha256(record: dict) -> str:
    """
    Backfill artifact_sha256 for a v0 iteration record.

    The artifact is defined as the (code, exec_output) pair —
    the generated program and its runtime evidence.
    Metadata (hypothesis, score, timestamp, iteration) is excluded.
    External files in exec_result.artifacts are NOT folded in;
    they get their own per-file hashes in Track C.
    """
    exec_result = record.get("exec_result") or {}
    artifact_core = {
        "code": record.get("code", ""),
        "exec_output": exec_result.get("output", ""),
        "exec_status": exec_result.get("status", ""),
        "exec_error": exec_result.get("error"),
    }
    canonical = json.dumps(artifact_core, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()



def migrate_record(record: dict) -> tuple[dict, MigrationOutcome]:
    """
    Pure function. Lifts a v0 record to v1, or passes a v1 record through.

    Returns the (possibly new) record and an outcome marker.
    Does not mutate the input.
    """
    version = record.get("schema_version", LEGACY_SCHEMA_VERSION)

    if version == CURRENT_SCHEMA_VERSION:
        return record, MigrationOutcome.ALREADY_CURRENT

    if version > CURRENT_SCHEMA_VERSION:
        # Record is from a future schema; we cannot safely downgrade.
        return record, MigrationOutcome.UNMIGRATABLE

    if version == LEGACY_SCHEMA_VERSION:
        lifted = {
            **record,
            "schema_version": CURRENT_SCHEMA_VERSION,
            "schema_status": SCHEMA_STATUS_MIGRATED,
            "artifact_sha256": _compute_legacy_sha256(record),
        }
        return lifted, MigrationOutcome.MIGRATED

    # Unknown intermediate version — refuse to guess.
    return record, MigrationOutcome.UNMIGRATABLE


def _atomic_write_json(path: Path, payload: dict) -> None:
    """Write JSON atomically: tmp file in same dir, fsync, rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, sort_keys=True, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        # Clean up temp file on failure.
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise


def migrate_all(
    paths: Iterable[Path],
    *,
    dry_run: bool = True,
) -> MigrationReport:
    """
    Migrate a collection of record files in place.

    Defaults to dry_run=True. When dry_run is False, each migrated record
    is written back atomically (tmp file, fsync, rename in same directory).

    Records that are already current or unmigratable are left untouched
    on disk.
    """
    total = 0
    already = 0
    migrated = 0
    unmig = 0

    for p in paths:
        total += 1
        with open(p, "r", encoding="utf-8") as f:
            record = json.load(f)

        new_record, outcome = migrate_record(record)

        if outcome is MigrationOutcome.ALREADY_CURRENT:
            already += 1
        elif outcome is MigrationOutcome.MIGRATED:
            migrated += 1
            if not dry_run:
                _atomic_write_json(p, new_record)
        elif outcome is MigrationOutcome.UNMIGRATABLE:
            unmig += 1

    return MigrationReport(
        total=total,
        already_current=already,
        migrated=migrated,
        unmigratable=unmig,
        dry_run=dry_run,
    )
