import json

from core.ai_engine import AIEngine, AIEngineError
from core.openai_engine import OpenAIEngine, OpenAIEngineError


def load_config() -> dict:
    with open("nova_config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    config = load_config()
    engine_mode = config.get("engine", "local").lower()

    try:
        if engine_mode == "openai":
            engine = OpenAIEngine()
            print("[Nova] Using OpenAI engine")
        else:
            engine = AIEngine()
            print("[Nova] Using LM Studio engine")
    except (AIEngineError, OpenAIEngineError) as exc:
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

        try:
            response = engine.generate(
                user_input,
                system_prompt=config.get("system_prompt")
            )
            print(f"\nNOVA: {response}\n")
        except (AIEngineError, OpenAIEngineError) as exc:
            print(f"\n[ERROR] {exc}\n")
        
if __name__ == "__main__":
    main()