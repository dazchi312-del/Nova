from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx


class AIEngineError(Exception):
    """Raised when LM Studio integration fails."""


class AIEngine:
    def __init__(self, config_path: str = "nova_config.json") -> None:
        self.config = self._load_config(config_path)

        lm = self.config["lm_studio"]
        generation = self.config["generation"]

        self.base_url: str = lm["base_url"].rstrip("/")
        self.chat_endpoint: str = lm["chat_endpoint"]
        self.model: str = lm["model"]
        self.timeout_seconds: int = lm["timeout_seconds"]

        self.default_temperature: float = generation["temperature"]
        self.default_max_tokens: int = generation["max_tokens"]
        self.default_stream: bool = generation["stream"]

        self.system_prompt: str = self.config["system_prompt"]
        self.url: str = f"{self.base_url}{self.chat_endpoint}"

    def _load_config(self, config_path: str) -> dict[str, Any]:
        path = Path(config_path)

        if not path.exists():
            raise AIEngineError(f"Missing config file: {config_path}")

        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise AIEngineError(f"Invalid JSON in config file: {exc}") from exc

    def generate(
        self,
        user_input: str,
        *,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        stream: bool | None = None,
    ) -> str:
        if not user_input or not user_input.strip():
            raise AIEngineError("User input is empty.")

        generation = self.config["generation"]

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt or self.system_prompt,
                },
                {
                    "role": "user",
                    "content": user_input.strip(),
                },
            ],
            "temperature": self.default_temperature if temperature is None else temperature,
            "max_tokens": self.default_max_tokens if max_tokens is None else max_tokens,
            "stream": self.default_stream if stream is None else stream,
            "top_p": generation.get("top_p", 0.9),
            "frequency_penalty": generation.get("frequency_penalty", 0.0),
            "presence_penalty": generation.get("presence_penalty", 0.0),
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(self.url, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise AIEngineError("LM Studio request timed out.") from exc
        except httpx.HTTPStatusError as exc:
            raise AIEngineError(
                f"LM Studio returned HTTP {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise AIEngineError(f"LM Studio connection failed: {exc}") from exc
        except ValueError as exc:
            raise AIEngineError(f"Invalid JSON response from LM Studio: {exc}") from exc

        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise AIEngineError(f"Unexpected LM Studio response structure: {data}") from exc