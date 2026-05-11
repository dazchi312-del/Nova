"""Tool package surface.

Provides lazy attribute access to canonical tool functions. The canonical
definition site is ``nova.core.tools``; this module re-exports them under
``nova.tools.<name>`` for convenience and as a stable patch point.

Lazy via ``__getattr__`` to avoid import cost at package load.
"""

from __future__ import annotations

import importlib
from typing import Any

_CANONICAL_MODULE = "nova.core.tools"

_TOOL_NAMES: tuple[str, ...] = (
    "read_file",
    "write_file",
    "list_directory",
    "run_shell",
    "list_processes",
    "kill_process",
    "get_system_stats",
)


def __getattr__(name: str) -> Any:
    if name not in _TOOL_NAMES:
        raise AttributeError(f"module 'nova.tools' has no attribute {name!r}")
    return getattr(importlib.import_module(_CANONICAL_MODULE), name)


def __dir__() -> list[str]:
    return list(_TOOL_NAMES)
