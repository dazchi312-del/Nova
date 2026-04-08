import json

from core.ai_engine import AIEngine
from core.errors import NovaEngineError
from core.openai_engine import OpenAIEngine, OpenAIEngineError
from core.memory import Memory
from core.reflector import Reflector

def load_config() -> dict:
    with open("nova_config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def main() -> None:
    config = load_config()
    engine_mode = config.get("engine", "local").lower()

    memory = Memory()
    print("[Nova] Memory core online.")

    reflector = Reflector()
    print("[Nova] Reflector online.")

    try:
        if engine_mode == "openai":
            engine = OpenAIEngine()
            print("[Nova] Using OpenAI engine")
        else:
            engine = AIEngine()
            print("[Nova] Using LM Studio engine")
    except (NovaEngineError, OpenAIEngineError) as exc:
        print(f"[ERROR] {exc}")
        return

    print("NOVA online. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("NOVA shutting down.")
            break

        if not user_input:
            print("[ERROR] Empty input.\n")
            continue

        persistent_context = {}
        for key in memory.list_keys():
            if key != "short_term_history":
                persistent_context[key] = memory.load(key)

        history_data = memory.load("short_term_history") or {}
        recent_history = history_data.get("log", []) if history_data else []

        base_prompt = config.get("system_prompt", "You are Nova.")
        memory_block = (
            f"\n\n--- SYSTEM MEMORY ---\n"
            f"Persistent Facts: {json.dumps(persistent_context)}\n"
            f"Recent History: {json.dumps(recent_history)}"
        )
        dynamic_system_prompt = base_prompt + memory_block

        try:
            response = engine.generate(
                user_input,
                system_prompt=dynamic_system_prompt
            )

            result = reflector.reflect(response)
            if not result.passed:
                print(f"\n[Nova] ⚠ Reflection warning: {result.reason}")

            print(f"\nNOVA: {response}\n")

            recent_history.append({"user": user_input, "nova": response})
            recent_history = recent_history[-5:]
            memory.save("short_term_history", {"log": recent_history})

        except (NovaEngineError, OpenAIEngineError) as exc:
            print(f"\n[ERROR] {exc}\n")

if __name__ == "__main__":
    main()
