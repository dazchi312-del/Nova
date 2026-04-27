"""Tests for EpisodicStore."""

import pytest
from nova.core.episode import Episode
from nova.core.episodic import EpisodicStore


@pytest.fixture
def store(tmp_path):
    s = EpisodicStore(tmp_path / "test.db")
    yield s
    s.close()


class TestAppend:
    def test_append_new_returns_true(self, store):
        e = Episode(timestamp="2026-01-01T00:00:00Z", content="hello", context={})
        assert store.append(e) is True

    def test_append_duplicate_returns_false(self, store):
        e = Episode(timestamp="2026-01-01T00:00:00Z", content="hello", context={})
        store.append(e)
        assert store.append(e) is False

    def test_count_after_appends(self, store):
        for i in range(5):
            store.append(Episode(timestamp=f"2026-01-01T00:00:0{i}Z",
                                 content=f"e{i}", context={}))
        assert store.count() == 5

    def test_dedup_does_not_grow_count(self, store):
        e = Episode(timestamp="2026-01-01T00:00:00Z", content="x", context={})
        for _ in range(10):
            store.append(e)
        assert store.count() == 1


class TestRetrieval:
    def test_get_returns_equivalent_episode(self, store):
        e = Episode(timestamp="2026-01-01T00:00:00Z",
                    content="hello", context={"k": "v"})
        store.append(e)
        retrieved = store.get(e.hash)
        assert retrieved is not None
        assert retrieved.hash == e.hash
        assert retrieved.verify()

    def test_get_missing_returns_none(self, store):
        assert store.get("0" * 64) is None

    def test_all_yields_in_timestamp_order(self, store):
        timestamps = ["2026-01-03T00:00:00Z",
                      "2026-01-01T00:00:00Z",
                      "2026-01-02T00:00:00Z"]
        for t in timestamps:
            store.append(Episode(timestamp=t, content="x", context={}))
        result = [e.timestamp for e in store.all()]
        assert result == sorted(timestamps)

    def test_by_kind_filters(self, store):
        store.append(Episode(timestamp="2026-01-01T00:00:00Z",
                             kind="observation", content="a", context={}))
        store.append(Episode(timestamp="2026-01-01T00:00:01Z",
                             kind="reflection", content="b", context={}))
        store.append(Episode(timestamp="2026-01-01T00:00:02Z",
                             kind="observation", content="c", context={}))
        obs = list(store.by_kind("observation"))
        assert len(obs) == 2
        assert all(e.kind == "observation" for e in obs)

    def test_since_filters(self, store):
        for i in range(5):
            store.append(Episode(timestamp=f"2026-01-0{i+1}T00:00:00Z",
                                 content=f"e{i}", context={}))
        results = list(store.since("2026-01-03T00:00:00Z"))
        assert len(results) == 3


class TestPersistence:
    def test_data_survives_reopen(self, tmp_path):
        path = tmp_path / "persist.db"
        s1 = EpisodicStore(path)
        e = Episode(timestamp="2026-01-01T00:00:00Z", content="durable", context={})
        s1.append(e)
        s1.close()

        s2 = EpisodicStore(path)
        assert s2.count() == 1
        retrieved = s2.get(e.hash)
        assert retrieved is not None
        assert retrieved.verify()
        s2.close()

    def test_wal_mode_enabled(self, store):
        mode = store._conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode.lower() == "wal"

    def test_parent_directory_created(self, tmp_path):
        nested = tmp_path / "a" / "b" / "c" / "store.db"
        s = EpisodicStore(nested)
        assert nested.parent.exists()
        s.close()


class TestIntegrity:
    def test_complex_context_roundtrips(self, store):
        ctx = {"nested": {"list": [1, 2, 3], "null": None}, "unicode": "café"}
        e = Episode(timestamp="2026-01-01T00:00:00Z", content="x", context=ctx)
        store.append(e)
        retrieved = store.get(e.hash)
        assert retrieved.context == ctx
        assert retrieved.verify()

    def test_hash_stable_across_storage(self, store):
        e = Episode(timestamp="2026-01-01T00:00:00Z",
                    content="café", context={"k": "naïve"})
        original_hash = e.hash
        store.append(e)
        retrieved = store.get(original_hash)
        assert retrieved.hash == original_hash


class TestContextManager:
    def test_context_manager_closes(self, tmp_path):
        with EpisodicStore(tmp_path / "ctx.db") as s:
            s.append(Episode(timestamp="2026-01-01T00:00:00Z",
                             content="x", context={}))
            assert s.count() == 1
