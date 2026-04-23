# sandbox.py v2.0.0
# Location: nova/core/sandbox.py
# Purpose: Docker + gVisor isolated execution for LLM-generated code

import subprocess
import tempfile
import os
from pathlib import Path
import shutil

# === CONFIGURATION ===
SANDBOX_DIR = Path(__file__).parent.parent / "labs" / "sandbox"
EXECUTION_TIMEOUT = 30  # seconds
DOCKER_IMAGE = "python:3.11-slim"
DOCKER_RUNTIME = "runsc"  # gVisor

# Modules that are explicitly blocked (pre-flight check)
BLOCKED_MODULES = {
    'os', 'sys', 'subprocess', 'shutil', 'pathlib',
    'socket', 'requests', 'urllib', 'http',
    'pickle', 'shelve', 'sqlite3',
    'importlib', 'builtins', '__builtins__',
    'ctypes', 'multiprocessing', 'threading',
    'code', 'codeop', 'compile'
}

BLOCKED_BUILTINS = {
    'eval', 'exec', 'compile', '__import__',
    'open', 'input', 'breakpoint',
    'globals', 'locals', 'vars',
    'getattr', 'setattr', 'delattr'
}


def ensure_sandbox_dir():
    """Create sandbox directory if it doesn't exist."""
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    return SANDBOX_DIR


def validate_code_safety(code: str) -> tuple[bool, str]:
    """
    Static analysis before Docker execution.
    AST Shield runs separately; this catches obvious patterns.
    """
    for module in BLOCKED_MODULES:
        patterns = [
            f'import {module}',
            f'from {module}',
            f"__import__('{module}'",
            f'__import__("{module}"'
        ]
        for pattern in patterns:
            if pattern in code:
                return False, f"Blocked import: {module}"

    for builtin in BLOCKED_BUILTINS:
        if f'{builtin}(' in code:
            return False, f"Blocked builtin: {builtin}()"

    return True, "Passed pre-flight checks"


def execute_sandboxed(code: str, timeout: int = None) -> dict:
    """
    Execute code in Docker container with gVisor isolation.
    
    Args:
        code: Python code to execute
        timeout: Optional timeout override (default: EXECUTION_TIMEOUT)
    
    Returns:
        dict with status, output, error, artifacts
    """
    timeout = timeout or EXECUTION_TIMEOUT

    # Step 1: Pre-flight safety check
    is_safe, msg = validate_code_safety(code)
    if not is_safe:
        return {
            "status": "blocked",
            "output": None,
            "error": f"Safety check failed: {msg}",
            "artifacts": []
        }

    # Step 2: Syntax validation
    try:
        compile(code, '<sandbox>', 'exec')
    except SyntaxError as e:
        return {
            "status": "syntax_error",
            "output": None,
            "error": f"Line {e.lineno}: {e.msg}",
            "artifacts": []
        }

    # Step 3: Prepare sandbox directory
    sandbox_dir = ensure_sandbox_dir()
    
    # Clear old artifacts
    for f in sandbox_dir.glob('*'):
        if f.is_file():
            f.unlink()

    # Step 4: Write code to temp file
    code_file = sandbox_dir / "user_code.py"
    
    wrapped_code = f'''
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# User code
{code}
'''
    code_file.write_text(wrapped_code, encoding='utf-8')

    # Step 5: Build Docker command
    docker_cmd = [
        "docker", "run",
        "--rm",
        f"--runtime={DOCKER_RUNTIME}",
        "--network=none",
        "--memory=512m",
        "--cpus=1",
        "--read-only",
        "--tmpfs", "/tmp:size=64m",
        "-v", f"{sandbox_dir.resolve()}:/sandbox:rw",
        "-w", "/sandbox",
        DOCKER_IMAGE,
        "python", "/sandbox/user_code.py"
    ]

    # Step 6: Execute in Docker
    try:
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )

        # Collect artifacts
        artifacts = [
            f.name for f in sandbox_dir.glob('*') 
            if f.is_file() and f.name != "user_code.py"
        ]

        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout[:3000] if result.stdout else None,
            "error": result.stderr[:500] if result.stderr else None,
            "return_code": result.returncode,
            "artifacts": artifacts
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "output": None,
            "error": f"Execution exceeded {timeout}s limit",
            "artifacts": []
        }

    except FileNotFoundError:
        return {
            "status": "docker_missing",
            "output": None,
            "error": "Docker not available. Start dockerd in WSL.",
            "artifacts": []
        }

    except Exception as e:
        return {
            "status": "exception",
            "output": None,
            "error": str(e),
            "artifacts": []
        }

    finally:
        # Clean up code file
        try:
            code_file.unlink()
        except:
            pass


def get_artifact_path(filename: str) -> Path:
    """Get full path to an artifact in the sandbox."""
    return SANDBOX_DIR / filename


# === TEST ===
if __name__ == "__main__":
    print("=== Sandbox v2.0.0 (Docker + gVisor) ===\n")
    
    # Test 1: Safe code
    safe_code = '''
print("Hello from gVisor sandbox!")
import math
print(f"Pi = {math.pi}")
'''
    print("Test 1: Safe code")
    result = execute_sandboxed(safe_code)
    print(f"Status: {result['status']}")
    print(f"Output: {result['output']}")
    print()

    # Test 2: Blocked import
    dangerous_code = '''
import os
os.system("whoami")
'''
    print("Test 2: Blocked import")
    result = execute_sandboxed(dangerous_code)
    print(f"Status: {result['status']}")
    print(f"Error: {result['error']}")
    print()

    # Test 3: Timeout test
    print("Test 3: Timeout (5s limit)")
    slow_code = '''
import time
time.sleep(10)
'''
    result = execute_sandboxed(slow_code, timeout=5)
    print(f"Status: {result['status']}")
    print(f"Error: {result['error']}")

