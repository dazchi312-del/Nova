from pathlib import Path
from typing import Optional
import sys
import json 
import hashlib
from pathlib import Path
from collections import Counter


DEFAULT_RECORDS_PATH = Path("experiments")

def resolve_path(user_input: Optional[str]) -> Path:
    if user_input is not None: 
        path = Path(user_input)
    else:
        path = DEFAULT_RECORDS_PATH
    
    if not path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        sys.exit(2)

    return path 

def load_records(path: Path) -> tuple[list[tuple[Path, dict]], list[Path]]:
    records = []
    errors = []
    files = path.rglob("*_record.json")
    
    for file in files:
        try:
            with open(file) as f:
                data = json.load(f)
            records.append((file, data))
        except (json.JSONDecodeError, OSError):
            errors.append(file)
    
    return records, errors


def verify(records: list[tuple[Path, dict]]) -> list[dict]:
    results = []
    for file_path, data in records:
        if "code" not in data or "code_hash" not in data:
            results.append({
                "path": file_path,
                "status": "malformed",
                "stored_hash": "",
                "computed_hash": "",
                "iteration": data.get("iteration", -1),
            })
            continue
        if data["code"] == "" and data["code_hash"] == "":
            results.append({
                "path": file_path,
                "status": "no_artifact",
                "stored_hash": "",
                "computed_hash": "",
                "iteration": data.get("iteration", -1),
            })
            continue
        computed = hashlib.sha256(data["code"].encode("utf-8")).hexdigest()[:16]
        stored = data["code_hash"]
        status = "ok" if computed == stored else "hash_mismatch"
        results.append({
            "path": file_path,
            "status": status,
            "stored_hash": stored,
            "computed_hash": computed,
            "iteration": data.get("iteration", -1),
        })
    return results
if __name__ == "__main__":
    path_arg = sys.argv[1] if len(sys.argv) > 1 else ""
    path = resolve_path(path_arg)
    records, load_errors = load_records(path)
    results = verify(records)
    
    counts = Counter(r["status"] for r in results)
    failures = [r for r in results if r["status"] != "ok"]
    total = len(results)
    
total_failures = len(failures) + len(load_errors)

print(f"Verified {total} records: "
      f"{counts['ok']} ok, "
      f"{counts['hash_mismatch']} hash_mismatch, "
      f"{counts['no_artifact']} no_artifact, "
      f"{counts['malformed']} malformed")

if load_errors:
    print(f"  ({len(load_errors)} files could not be loaded)")

true_failures = [r for r in failures if r["status"] != "no_artifact"]
no_artifacts = [r for r in failures if r["status"] == "no_artifact"]

if true_failures or load_errors:
    print("\nFAILURES:")
    for r in true_failures:
        if r["status"] == "hash_mismatch":
            print(f"  {r['path'].name} — hash_mismatch "
                  f"(stored={r['stored_hash']}, computed={r['computed_hash']})")
        else:
            print(f"  {r['path'].name} — {r['status']}")
    for err_path in load_errors:
        print(f"  {err_path.name} — load_error")

if no_artifacts:
    print(f"\nLEGACY (pre-provenance, no artifact stored): {len(no_artifacts)} records")

sys.exit(0 if not (true_failures or load_errors) else 1)


    


        

    


