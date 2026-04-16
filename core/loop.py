# core/loop.py
import json
import requests

# ── Config ──────────────────────────────────────────────
with open("nova_config.json") as f:
    cfg = json.load(f)

PRIMARY_URL   = cfg["base_url"]
PRIMARY_MODEL = cfg["primary_model"]
REFLECT_URL   = cfg["reflector"]["base_url"]
REFLECT_MODEL = cfg["reflector"]["model"]

# ── One call to Nemotron 70B ─────────────────────────────
def call_primary(prompt):
    print("[Primary] Calling Nemotron 70B...")
    r = requests.post(
        f"{PRIMARY_URL}/chat/completions",
        json={
            "model": PRIMARY_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 512
        }
    )
    return r.json()["choices"][0]["message"]["content"]

# ── One call to Reflector 8B on MacBook ─────────────────
def call_reflector(original, response):
    print("[Reflector] Calling llama3.1:8b on MacBook...")
    payload = {
        "model": REFLECT_MODEL,
        "prompt": f"Rate this response for accuracy 0.0-1.0.\nQ: {original}\nA: {response}\nScore only, one decimal:",
        "stream": False
    }
    r = requests.post(f"{REFLECT_URL}/api/generate", json=payload)
    return r.json()["response"].strip()

# ── Main Loop ────────────────────────────────────────────
if __name__ == "__main__":
    print("Nova Minimal Loop — type 'exit' to quit\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break

        # Step 1 — Primary generates
        response = call_primary(user_input)
        print(f"\nNova: {response}\n")

        # Step 2 — Reflector scores
        score = call_reflector(user_input, response)
        print(f"[Reflector] Score: {score}\n")
