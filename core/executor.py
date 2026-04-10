"""
Nova Executor - Layer 4
Runs code files and captures output + errors
Clean, safe, precise
"""

import subprocess
import sys
import os
from pathlib import Path
from core.logger import log


class ExecutionResult:
    """The result of running a piece of code"""

    def __init__(self, success: bool, output: str, error: str, returncode: int):
        self.success = success
        self.output = output.strip()
        self.error = error.strip()
        self.returncode = returncode

    def __str__(self):
        if self.success:
            return f"[OK] Success\n{self.output}"
        else:
            return f"[FAIL] Failed (code {self.returncode})\n{self.error}"


class Executor:
    """
    Nova's code execution engine.
    Runs Python files safely and returns structured results.
    """

    # Allowed environment variables passed to subprocess
    _SAFE_ENV_KEYS = {"SYSTEMROOT", "PATH", "TEMP", "TMP", "USERPROFILE"}

    def __init__(self, workspace: str = "C:/Users/dazch/nova"):
        self.workspace = Path(workspace)
        self.python = sys.executable
        log("CODE", f"Executor ready: {self.python}")

    def _safe_env(self) -> dict:
        """Return a minimal environment - strips API keys and Nova internals."""
        return {
            k: v for k, v in os.environ.items()
            if k in self._SAFE_ENV_KEYS
        }

    def run_file(self, filepath: str, timeout: int = 30) -> ExecutionResult:
        """Run a Python file and return the result"""
        path = Path(filepath)

        if not path.exists():
            log("CODE", f"File not found: {filepath}")
            return ExecutionResult(
                success=False,
                output="",
                error=f"File not found: {filepath}",
                returncode=-1
            )

        log("CODE", f"Executing: {path.name}")

        try:
            result = subprocess.run(
                [self.python, str(path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.workspace),
                env=self._safe_env()
            )

            success = result.returncode == 0

            if success:
                log("CODE", f"Execution success: {path.name}")
            else:
                log("CODE", f"Execution failed: {path.name} (code {result.returncode})")

            return ExecutionResult(
                success=success,
                output=result.stdout,
                error=result.stderr,
                returncode=result.returncode
            )

        except subprocess.TimeoutExpired:
            log("CODE", f"Timeout: {path.name}")
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution timed out after {timeout}s",
                returncode=-1
            )

        except Exception as e:
            log("CODE", f"Executor error: {e}")
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                returncode=-1
            )

    def run_code(self, code: str, filename: str = "nova_temp.py") -> ExecutionResult:
        """Write code to a temp file, run it, then clean up."""
        temp_path = self.workspace / "temp" / filename
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(code)
            log("CODE", f"Temp file written: {filename}")
            return self.run_file(str(temp_path))

        except Exception as e:
            log("CODE", f"Failed to write temp file: {e}")
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                returncode=-1
            )

        finally:
            if temp_path.exists():
                temp_path.unlink()
                log("CODE", f"Temp file cleaned: {filename}")
