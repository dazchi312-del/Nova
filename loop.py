from __future__ import annotations

import requests
from core.config import config
from core.dispatcher import dispatch, TOOL_SCHEMA, DispatchError

# --- Pull from config ---
_lm = config.get("lm_studio", {})
_gen = config.get("generation", {})

LM_STUDIO_URL = _lm.get("base_url", "http://localhost:1234") + _lm.get("chat_endpoint", "/v1/chat/completions")
MODEL = _lm.get("model", "llama-3.1-8b-instruct")
TIMEOUT = _lm.get("timeout_seconds", 60)
TEMPERATURE = _gen.get("temperature", 0.3)
MAX_TOKENS = _gen.get("max_tokens", 1024)
STREAM = _gen.get("stream", False)

MAX_TOOL_ROUNDS = 5

# --- Two-message system prompt (Identity + Tool Schema) ---
SYSTEM_MESSAGES = [
    {
        "role": "system",
        "content": config.get("system_prompt", "You are Nova, a local AI agent.")
    },
    {
        "role": "system",
        "content": f"[TOOL SCHEMA]\n{TOOL_SCHEMA}\n[/TOOL SCHEMA]"
    }
]


def chat(messages: list[dict], temperature: float | None = None) -> str:
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature if temperature is not None else TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": STREAM,
    }
    response = requests.post(LM_STUDIO_URL, json=payload, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def run_loop(user_input: str, history: list[dict] | None = None) -> str:
    messages = list(SYSTEM_MESSAGES)
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_input})

    for round_num in range(MAX_TOOL_ROUNDS):
        nova_reply = chat(messages)
        tool_called, result = dispatch(nova_reply)

        if not tool_called:
            return nova_reply

        # Tool was called — feed result back to Nova
        messages.append({"role": "assistant", "content": nova_reply})
        messages.append({"role": "user", "content": f"[TOOL RESULT]\n{result}\n[/TOOL RESULT]"})

    return "[LOOP ERROR] Max tool rounds reached without final response."
