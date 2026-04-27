"""
Episodic Store — append-only SQLite persistence for Episodes.

Convention: callers supply an explicit path. Recommended location is
~/nova/data/episodic.db, but the store itself is path-agnostic so tests
and alternate deployments can override freely.

Design invariants:
  - Append-only: no update or delete methods exist.
  - Idempotent: re-appending an identical Episode is a silent no-op
    (INSERT OR IGNORE on the hash primary key).
  - WAL mode: concurrent reads do not block writes.
  - Hash integrity: every retrieved Episode is verifiable via .verify().
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterator, Optional

from nova.core.episode import Episode


SCHEMA = """
CREATE TABLE IF NOT EXISTS episodes (
    hash       TEXT PRIMARY KEY,
    timestamp  TEXT NOT NULL,
    kind       TEXT NOT NULL,
    content    TEXT NOT NULL,
    context    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_episodes_timestamp ON episodes(timestamp);
CREATE INDEX IF NOT EXISTS idx_episodes_kind      ON episodes(kind);
"""


class EpisodicStore:
    """Append-only SQLite-backed store for Episodes."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path))
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    # ---- write ----

    def append(self, episode: Episode) -> bool:
        """Append an episode. Returns True if newly inserted, False if duplicate."""
        cur = self._conn.execute(
            "INSERT OR IGNORE INTO episodes (hash, timestamp, kind, content, context) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                episode.hash,
                episode.timestamp,
                episode.kind,
                json.dumps(episode.content, ensure_ascii=False),
                json.dumps(episode.context, ensure_ascii=False),
            ),
        )
        self._conn.commit()
        return cur.rowcount == 1

    # ---- read ----

    def get(self, hash_: str) -> Optional[Episode]:
        row = self._conn.execute(
            "SELECT timestamp, kind, content, context FROM episodes WHERE hash = ?",
            (hash_,),
        ).fetchone()
        if row is None:
            return None
        return self._row_to_episode(row)

    def all(self) -> Iterator[Episode]:
        cur = self._conn.execute(
            "SELECT timestamp, kind, content, context FROM episodes ORDER BY timestamp"
        )
        for row in cur:
            yield self._row_to_episode(row)

    def by_kind(self, kind: str) -> Iterator[Episode]:
        cur = self._conn.execute(
            "SELECT timestamp, kind, content, context FROM episodes "
            "WHERE kind = ? ORDER BY timestamp",
            (kind,),
        )
        for row in cur:
            yield self._row_to_episode(row)

    def since(self, timestamp: str) -> Iterator[Episode]:
        """Episodes with timestamp >= the given ISO-8601 string."""
        cur = self._conn.execute(
            "SELECT timestamp, kind, content, context FROM episodes "
            "WHERE timestamp >= ? ORDER BY timestamp",
            (timestamp,),
        )
        for row in cur:
            yield self._row_to_episode(row)

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]

    # ---- lifecycle ----

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "EpisodicStore":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ---- internal ----

    @staticmethod
    def _row_to_episode(row) -> Episode:
        timestamp, kind, content_json, context_json = row
        return Episode(
            timestamp=timestamp,
            kind=kind,
            content=json.loads(content_json),
            context=json.loads(context_json),
        )
