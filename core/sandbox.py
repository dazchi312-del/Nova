# sandbox.py v1.0.0
# Location: nova/core/sandbox.py
# Purpose: Hardened execution environment for LLM-generated code

import subprocess
import tempfile
import os
import sys
from pathlib import Path

# === CONFIGURATION ===
SANDBOX_DIR = Path(__file__).parent.parent / "labs" / "sandbox"
EXECUTION_TIMEOUT = 30  # seconds

# Modules the generated code is allowed to import
ALLOWED_MODULES = {
    'math', 'random', 'collections', 'itertools', 'functools',
    'numpy', 'matplotlib', 'matplotlib.pyplot',
    'json', 'datetime', 'time', 're', 'string',
    'statistics', 'decimal', 'fractions'
}

# Modules that are explicitly blocked
BLOCKED_MODULES = {
    'os', 'sys', 'subprocess', 'shutil', 'pathlib',
    'socket', 'requests', 'urllib', 'http',
    'pickle', 'shelve', 'sqlite3',
    'importlib', 'builtins', '__builtins__',
    'ctypes', 'multiprocessing', 'threading',
    'code', 'codeop', 'compile'
}

# Blocked built-in functions
BLOCKED_BUILTINS = {
    'eval', 'exec', 'compile', '__import__',
    'open', 'input', 'breakpoint',
    'globals', 'locals', 'vars',
    'getattr', 'setattr', 'delattr',
    'memoryview', 'credits', 'license'
}


def ensure_sandbox_dir():
    """Create sandbox directory if it doesn't exist."""
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    return SANDBOX_DIR


def validate_code_safety(code: str) -> tuple[bool, str]:
    """
    Static analysis to catch dangerous patterns before execution.
    Returns (is_safe, reason)
    """
    
    # Check for blocked module imports
    for module in BLOCKED_MODULES:
        patterns = [
            f'import {module}',
            f'from {module}',
            f"__import__('{module}'",
            f'__import__("{module}"'
        ]
        for pattern in patterns:
            if pattern in code:
                return False, f"Blocked import detected: {module}"
    
    # Check for blocked builtins
    for builtin in BLOCKED_BUILTINS:
        # Look for function calls
        if f'{builtin}(' in code:
            return False, f"Blocked builtin detected: {builtin}()"
    
    # Check for file system access patterns
    dangerous_patterns = [
        ('os.remove', 'File deletion'),
        ('os.unlink', 'File deletion'),
        ('os.rmdir', 'Directory deletion'),
        ('shutil.rmtree', 'Recursive deletion'),
        ('os.system', 'Shell command execution'),
        ('subprocess', 'Process spawning'),
        ('.write(', 'File writing'),  # Catches open().write()
        ('Path(', 'Path manipulation'),
    ]
    
    for pattern, reason in dangerous_patterns:
        if pattern in code:
            # Special case: allow matplotlib savefig
            if pattern == '.write(' and 'savefig' in code:
                continue
            return False, f"Dangerous pattern: {reason} ({pattern})"
    
    # Check for network access
    network_patterns = ['socket', 'urlopen', 'requests.', 'http.client']
    for pattern in network_patterns:
        if pattern in code:
            return False, f"Network access not allowed: {pattern}"
    
    return True, "Code passed safety checks"


def build_sandboxed_code(code: str) -> str:
    """
    Wrap user code with safety restrictions and output capture.
    """
    
    sandbox_dir = ensure_sandbox_dir()
    
    wrapper = f'''
# === SANDBOX WRAPPER ===
import sys
import io
import os

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Lock working directory to sandbox
os.chdir(r"{sandbox_dir}")

# Restrict what matplotlib can do
import matplotlib
matplotlib.use('Agg')  # No GUI, file output only
import matplotlib.pyplot as plt

# Patch savefig to force sandbox directory
_original_savefig = plt.savefig
def _safe_savefig(fname, *args, **kwargs):
    from pathlib import Path
    safe_path = Path(r"{sandbox_dir}") / Path(fname).name
    _original_savefig(str(safe_path), *args, **kwargs)
    print(f"[SANDBOX] Saved: {{safe_path}}")
plt.savefig = _safe_savefig

# === USER CODE BEGINS ===
{code}
# === USER CODE ENDS ===

# Auto-close any open plots
plt.close('all')
'''
    return wrapper


def execute_sandboxed(code: str) -> dict:
    """
    Execute code in isolated environment with full safety checks.
    Returns dict with status, output, error, artifacts.
    """
    
    # Step 1: Static safety analysis
    is_safe, safety_msg = validate_code_safety(code)
    if not is_safe:
        return {
            "status": "blocked",
            "output": None,
            "error": f"Safety check failed: {safety_msg}",
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
    
    # Step 3: Prepare sandbox environment
    sandbox_dir = ensure_sandbox_dir()
    
    # Clear old artifacts
    for f in sandbox_dir.glob('*'):
        if f.is_file():
            f.unlink()
    
    # Step 4: Wrap code with safety measures
    wrapped_code = build_sandboxed_code(code)
    
    # Step 5: Write to temp file
    with tempfile.NamedTemporaryFile(
        mode='w', 
        suffix='.py', 
        delete=False, 
        encoding='utf-8',
        dir=sandbox_dir
    ) as f:
        f.write(wrapped_code)
        temp_path = f.name
    
    # Step 6: Execute in subprocess
    try:
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT,
            encoding='utf-8',
            errors='replace',
            cwd=str(sandbox_dir),
            env={
                **os.environ,
                'PYTHONIOENCODING': 'utf-8',
                'MPLCONFIGDIR': str(sandbox_dir)  # Isolate matplotlib config
            }
        )
        
        # Collect artifacts
        artifacts = [f.name for f in sandbox_dir.glob('*') if f.is_file() and not f.suffix == '.py']
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout[:3000],
            "error": result.stderr[:500] if result.stderr else None,
            "return_code": result.returncode,
            "artifacts": artifacts
        }
    
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "output": None,
            "error": f"Execution exceeded {EXECUTION_TIMEOUT}s limit",
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
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass


def get_artifact_path(filename: str) -> Path:
    """Get full path to an artifact in the sandbox."""
    return SANDBOX_DIR / filename


# === TEST ===
if __name__ == "__main__":
    # Test 1: Safe code
    safe_code = '''
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
plt.savefig('test_plot.png')
print("Generated sine wave plot")
'''
    
    print("=== Test 1: Safe code ===")
    result = execute_sandboxed(safe_code)
    print(f"Status: {result['status']}")
    print(f"Output: {result['output']}")
    print(f"Artifacts: {result['artifacts']}")
    
    # Test 2: Dangerous code
    dangerous_code = '''
import os
os.remove('important_file.txt')
'''
    
    print("\n=== Test 2: Dangerous code ===")
    result = execute_sandboxed(dangerous_code)
    print(f"Status: {result['status']}")
    print(f"Error: {result['error']}")
    
    # Test 3: Network attempt
    network_code = '''
import requests
requests.get('http://evil.com')
'''
    
    print("\n=== Test 3: Network code ===")
    result = execute_sandboxed(network_code)
    print(f"Status: {result['status']}")
    print(f"Error: {result['error']}")
