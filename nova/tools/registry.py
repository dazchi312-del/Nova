"""Tool registry — data-driven replacement for the dispatcher cascade.

The legacy `execute_tool()` in `nova/core/dispatcher.py` uses a hand-written
if/elif cascade to route tool names to functions. This module replaces that
cascade with a registry: each tool is a `ToolSpec` entry in `REGISTRY`, and
`dispatch_call()` looks up the spec by name and invokes it.

Behavior preserved exactly from the legacy cascade:
  - Unknown tool name -> DispatchError("Unknown tool: '<name>'")
  - Empty/missing tool name -> DispatchError("Tool call missing 'tool' field.")
  - ToolError from the tool function -> DispatchError(...) from exc
  - KeyError from missing args -> DispatchError(...) from exc
  - All other exceptions propagate unwrapped

The except-clause order (ToolError before KeyError) matches the legacy
dispatcher and is pinned by the characterization suite.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any, Callable

from nova.core.dispatcher import DispatchError
from nova.core.tools import ToolError  # noqa: F401  — re-export for clarity



# --- ToolSpec ---------------------------------------------------------------


@dataclass(frozen=True)
class ToolSpec:
    """Describes a callable tool exposed to the dispatcher.

    Attributes:
        name:        The string a model uses to invoke this tool.
        func_path:   Dotted import path to the tool function, resolved at
                     invoke time. Late binding lets tests patch the function
                     at its canonical module location.
        adapter: Callable[[dict[str, Any]], tuple[list[Any], dict[str, Any]]]

    """

    name: str
    func_path: str
    adapter: Callable[[dict[str, Any]], tuple[list[Any], dict[str, Any]]]

    def invoke(self, args: dict[str, Any]) -> str:
        module_path, _, attr = self.func_path.rpartition(".")
        module = importlib.import_module(module_path)
        func = getattr(module, attr)
        pos, kw = self.adapter(args)
        return func(*pos, **kw)




# --- Registry storage and registration --------------------------------------


REGISTRY: dict[str, ToolSpec] = {}


def register(spec: ToolSpec) -> None:
    """Add a ToolSpec to the registry. Raises ValueError on duplicate name."""
    if spec.name in REGISTRY:
        raise ValueError(f"Tool '{spec.name}' is already registered.")
    REGISTRY[spec.name] = spec


# --- Adapters ---------------------------------------------------------------
# One adapter per tool. Each takes the parsed args dict and returns the
# kwargs dict to splat into the tool function. Coercion and defaults live
# here, mirroring the legacy cascade line-for-line.


def _adapt_read_file(args: dict[str, Any]) -> tuple[list, dict]:
    return ([args["path"]], {})

def _adapt_write_file(args: dict[str, Any]) -> tuple[list, dict]:
    return ([args["path"], args["content"]], {})

def _adapt_list_directory(args: dict[str, Any]) -> tuple[list, dict]:
    return ([args.get("path", ".")], {})

def _adapt_run_shell(args: dict[str, Any]) -> tuple[list, dict]:
    return ([args["command"]], {})

def _adapt_list_processes(args: dict[str, Any]) -> tuple[list, dict]:
    return ([], {
        "sort_by": args.get("sort_by", "cpu"),
        "limit": int(args.get("limit", 20)),
    })

def _adapt_kill_process(args: dict[str, Any]) -> tuple[list, dict]:
    return ([], {
        "pid": int(args["pid"]),
        "force": bool(args.get("force", False)),
    })

def _adapt_get_system_stats(args: dict[str, Any]) -> tuple[list, dict]:
    return ([], {})



# --- Tool registration ------------------------------------------------------
# Note: read_file/write_file/list_directory/run_shell were invoked
# positionally in the legacy cascade. We invoke them by keyword here, which
# is equivalent because their parameter names match the JSON arg names.


register(ToolSpec("read_file",        "nova.core.tools.read_file",         _adapt_read_file))
register(ToolSpec("write_file",       "nova.core.tools.write_file",        _adapt_write_file))
register(ToolSpec("list_directory",   "nova.core.tools.list_directory",    _adapt_list_directory))
register(ToolSpec("run_shell",        "nova.core.tools.run_shell",         _adapt_run_shell))
register(ToolSpec("list_processes",   "nova.core.tools.list_processes",    _adapt_list_processes))
register(ToolSpec("kill_process",     "nova.core.tools.kill_process",      _adapt_kill_process))
register(ToolSpec("get_system_stats", "nova.core.tools.get_system_stats",  _adapt_get_system_stats))



# --- Public dispatch entry point --------------------------------------------


def dispatch_call(call: dict[str, Any]) -> str:
    """Look up and invoke a tool from a parsed call dict.

    Args:
        call: A dict shaped like {"tool": "<name>", "args": {...}}.

    Returns:
        The string result from the tool function.

    Raises:
        DispatchError: If the tool name is missing, unknown, or if the tool
            raises ToolError or KeyError. Other exceptions propagate.
    """
    tool_name = call.get("tool", "").strip()
    args = call.get("args", {})

    if not tool_name:
        raise DispatchError("Tool call missing 'tool' field.")

    spec = REGISTRY.get(tool_name)
    if spec is None:
        raise DispatchError(f"Unknown tool: '{tool_name}'")

    try:
        return spec.invoke(args)
    except ToolError as exc:
        raise DispatchError(f"Tool '{tool_name}' failed: {exc}") from exc
    except KeyError as exc:
        raise DispatchError(f"Tool '{tool_name}' missing required arg: {exc}") from exc
