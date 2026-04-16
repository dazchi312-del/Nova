import sys
import subprocess
import os
from core.loop import chat

if __name__ == "__main__":
    # Auto-launch scheduler in background
    scheduler_path = os.path.join(os.path.dirname(__file__), "core", "scheduler.py")
    subprocess.Popen(
        [sys.executable, scheduler_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    if args:
        prompt = " ".join(args)
        response = chat(prompt)
        print(response)
    else:
        print("[Nova] Online. Type 'exit' to quit.")
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ("exit", "quit"):
                    print("[Nova] Shutting down.")
                    break
                if not user_input:
                    continue
                response = chat(user_input)
                print(f"Nova: {response}")
            except KeyboardInterrupt:
                print("\n[Nova] Interrupted. Shutting down.")
                break

