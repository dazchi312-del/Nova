# tests/test_embedder.py
"""Smoke tests for NomicEmbedder using httpx.MockTransport."""

from __future__ import annotations

import json

import httpx
import pytest

from nova.core.artifact import NOMIC_EMBED_DIM, NOMIC_MODEL_NAME
from nova.core.embedder import NomicEmbedder


def _make_client(handler) -> httpx.Client:
    transport = httpx.MockTransport(handler)
    return httpx.Client(transport=transport)


def test_embed_success():
    expected_vec = [0.01] * NOMIC_EMBED_DIM

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/embed"
        body = json.loads(request.content)
        assert body["model"] == NOMIC_MODEL_NAME
        assert body["input"] == "hello world"
        return httpx.Response(200, json={"embeddings": [expected_vec]})

    with NomicEmbedder(client=_make_client(handler)) as emb:
        result = emb.embed("hello world")

    assert result is not None
    assert result.dim == NOMIC_EMBED_DIM
    assert result.vector == expected_vec
    assert result.model == NOMIC_MODEL_NAME
    assert result.source_text == "hello world"
    assert result.generated_at  # ISO string present


def test_embed_truncates_long_input():
    long_text = "x" * 5000
    captured_input = {}

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        captured_input["input"] = body["input"]
        return httpx.Response(200, json={"embeddings": [[0.0] * NOMIC_EMBED_DIM]})

    with NomicEmbedder(client=_make_client(handler)) as emb:
        emb.embed(long_text)

    assert len(captured_input["input"]) == 2000  # EMBED_SOURCE_MAX_CHARS


def test_embed_empty_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        pytest.fail("should not call API on empty input")

    with NomicEmbedder(client=_make_client(handler)) as emb:
        assert emb.embed("") is None
        assert emb.embed("   ") is None


def test_embed_dim_mismatch_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"embeddings": [[0.1] * 512]})  # wrong dim

    with NomicEmbedder(client=_make_client(handler)) as emb:
        assert emb.embed("test") is None


def test_embed_malformed_response_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"embeddings": ["not-a-list"]})

    with NomicEmbedder(client=_make_client(handler)) as emb:
        assert emb.embed("test") is None


def test_embed_http_error_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="ollama exploded")

    with NomicEmbedder(client=_make_client(handler)) as emb:
        assert emb.embed("test") is None


def test_embed_timeout_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("simulated timeout")

    with NomicEmbedder(client=_make_client(handler)) as emb:
        assert emb.embed("test") is None


def test_embed_missing_embedding_key_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"other_key": "nope"})

    with NomicEmbedder(client=_make_client(handler)) as emb:
        assert emb.embed("test") is None
