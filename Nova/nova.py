"""
Nova launcher — run from project root.
Usage:
    python nova.py                        # interactive mode
    python nova.py "your prompt here"     # single prompt mode
    python nova.py --dry-run              # dry-run interactive mode
    python nova.py --dry-run "prompt"     # dry-run single prompt mode
"""
import sys
import argparse
from core.loop import run_loop, interactive_loop

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nova — Local AI Operating System")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview tool calls without executing them."
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Optional single prompt. If omitted, enters interactive mode."
    )

    args = parser.parse_args()
    dry_run = args.dry_run

    if dry_run:
        print("[DRY RUN MODE] Tool calls will be previewed, not executed.\n")

    if args.prompt:
        prompt = " ".join(args.prompt)
        response = run_loop(prompt, dry_run=dry_run)
        print(response)
    else:
        interactive_loop(dry_run=dry_run)
