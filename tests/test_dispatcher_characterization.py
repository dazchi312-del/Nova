"""
Characterization tests for nova.core.dispatcher.execute_tool.

These tests freeze the OBSERVED behavior of the dispatcher cascade as it
exists at commit f76aa31, prior to migration to the tool registry pattern.

They are not aspirational — they document reality, including any quirks
(arg coercion, default values, exception translation).

After migration to the registry, these tests must continue to pass
unchanged. If a test must change, that is a behavior change and requires
a separate, deliberate commit with explicit justification.

Reference: Plan C, Step C.0 (Tool Registry Migration).
"""
import pytest
from unittest.mock import patch

from nova.core.dispatcher import execute_tool
from nova.core.errors import DispatchError
from nova.core.errors import NovaToolError


# ---------------------------------------------------------------------------
# Routing: each of the 7 cascade branches dispatches to the correct function
# ---------------------------------------------------------------------------

class TestRoutingHappyPath:
    """Verify execute_tool routes tool_name → correct underlying function."""

    @patch("nova.core.tools.read_file", return_value="FILE_CONTENTS")
    def test_read_file_routes_with_path_arg(self, mock_read):
        result = execute_tool({"tool": "read_file", "args": {"path": "/x"}})
        assert result == "FILE_CONTENTS"
        mock_read.assert_called_once_with("/x")

    @patch("nova.core.tools.write_file", return_value="OK")
    def test_write_file_routes_with_path_and_content(self, mock_write):
        result = execute_tool({
            "tool": "write_file",
            "args": {"path": "/x", "content": "hello"},
        })
        assert result == "OK"
        mock_write.assert_called_once_with("/x", "hello")

    @patch("nova.core.tools.list_directory", return_value=["a", "b"])
    def test_list_directory_routes_with_default_path(self, mock_list):
        result = execute_tool({"tool": "list_directory", "args": {}})
        assert result == ["a", "b"]
        mock_list.assert_called_once_with(".")

    @patch("nova.core.tools.list_directory", return_value=["a"])
    def test_list_directory_routes_with_explicit_path(self, mock_list):
        execute_tool({"tool": "list_directory", "args": {"path": "core"}})
        mock_list.assert_called_once_with("core")

    @patch("nova.core.tools.run_shell", return_value="stdout")
    def test_run_shell_routes_with_command_arg(self, mock_shell):
        result = execute_tool({
            "tool": "run_shell",
            "args": {"command": "ls"},
        })
        assert result == "stdout"
        mock_shell.assert_called_once_with("ls")

    @patch("nova.core.tools.list_processes", return_value="proc table")
    def test_list_processes_routes_with_defaults(self, mock_lp):
        execute_tool({"tool": "list_processes", "args": {}})
        mock_lp.assert_called_once_with(sort_by="cpu", limit=20)

    @patch("nova.core.tools.list_processes", return_value="proc table")
    def test_list_processes_coerces_limit_to_int(self, mock_lp):
        execute_tool({
            "tool": "list_processes",
            "args": {"sort_by": "mem", "limit": "50"},
        })
        mock_lp.assert_called_once_with(sort_by="mem", limit=50)

    @patch("nova.core.tools.kill_process", return_value="killed")
    def test_kill_process_coerces_pid_and_force(self, mock_kp):
        execute_tool({
            "tool": "kill_process",
            "args": {"pid": "1234", "force": 1},
        })
        mock_kp.assert_called_once_with(pid=1234, force=True)

    @patch("nova.core.tools.kill_process", return_value="killed")
    def test_kill_process_force_defaults_to_false(self, mock_kp):
        execute_tool({"tool": "kill_process", "args": {"pid": 9}})
        mock_kp.assert_called_once_with(pid=9, force=False)

    @patch("nova.core.tools.get_system_stats", return_value="stats")
    def test_get_system_stats_routes_no_args(self, mock_stats):
        result = execute_tool({"tool": "get_system_stats", "args": {}})
        assert result == "stats"
        mock_stats.assert_called_once_with()


# ---------------------------------------------------------------------------
# Error contract: dispatcher's exception translation behavior
# ---------------------------------------------------------------------------

class TestErrorContract:
    """Verify execute_tool's exception translation contract."""

    def test_missing_tool_field_raises_dispatch_error(self):
        with pytest.raises(DispatchError, match="missing 'tool' field"):
            execute_tool({"args": {}})

    def test_empty_tool_name_raises_dispatch_error(self):
        with pytest.raises(DispatchError, match="missing 'tool' field"):
            execute_tool({"tool": "", "args": {}})

    def test_whitespace_tool_name_raises_dispatch_error(self):
        with pytest.raises(DispatchError, match="missing 'tool' field"):
            execute_tool({"tool": "   ", "args": {}})

    def test_unknown_tool_raises_dispatch_error_with_name(self):
        with pytest.raises(DispatchError, match="Unknown tool: 'bogus'"):
            execute_tool({"tool": "bogus", "args": {}})

    @patch("nova.core.tools.read_file", side_effect=NovaToolError("disk full"))
    def test_tool_error_wrapped_in_dispatch_error(self, _mock):
        with pytest.raises(DispatchError, match="Tool 'read_file' failed: disk full"):
            execute_tool({"tool": "read_file", "args": {"path": "/x"}})

    def test_missing_required_arg_wrapped_in_dispatch_error(self):
        # read_file requires "path"; omitting it triggers KeyError → DispatchError
        with pytest.raises(DispatchError, match="missing required arg"):
            execute_tool({"tool": "read_file", "args": {}})

    def test_dispatch_error_chains_original_keyerror(self):
        with pytest.raises(DispatchError) as exc_info:
            execute_tool({"tool": "read_file", "args": {}})
        assert isinstance(exc_info.value.__cause__, KeyError)

    @patch("nova.core.tools.read_file", side_effect=NovaToolError("boom"))
    def test_dispatch_error_chains_original_tool_error(self, _mock):
        with pytest.raises(DispatchError) as exc_info:
            execute_tool({"tool": "read_file", "args": {"path": "/x"}})
        assert isinstance(exc_info.value.__cause__, NovaToolError)
