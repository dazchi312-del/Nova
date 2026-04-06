from core.ai_engine import AIEngine, AIEngineError


def main() -> None:
    engine = AIEngine()

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
            response = engine.generate(user_input)
            print(f"\nNOVA: {response}\n")
        except AIEngineError as exc:
            print(f"\n[ERROR] {exc}\n")


if __name__ == "__main__":
    main()