from unittest.mock import patch
from ruffit.watcher import PyFileMonitor
import ruffit.utils as utils


class DummyEvent:
    def __init__(self, src_path, is_directory=False):
        self.src_path = src_path
        self.is_directory = is_directory


def test_on_modified_triggers_utils(tmp_path):
    monitor = PyFileMonitor()
    file_path = tmp_path / "test.py"
    file_path.write_text("print('hi')")
    event = DummyEvent(str(file_path))
    with (
        patch("ruffit.watcher.run_ruff_format") as mock_format,
        patch("ruffit.watcher.run_ruff_check") as mock_ruff,
        patch("ruffit.watcher.run_ty_check") as mock_ty,
        patch.object(monitor, "console") as mock_console,
        patch.object(monitor, "_should_ignore", return_value=False),
        patch.object(monitor, "_debounced", return_value=False),
    ):
        monitor.on_modified(event)  # type: ignore
        # Check that a Panel with the correct text is printed
        found = False
        for call in mock_console.print.call_args_list:
            panel = call.args[0]
            if hasattr(panel, "renderable") and "Modified:" in str(panel.renderable) and str(file_path) in str(panel.renderable):
                found = True
        assert found, "Expected Panel with 'Modified:' and file path not found in console output"
        mock_format.assert_called_once_with(str(file_path), monitor.console)
        mock_ruff.assert_called_once_with(str(file_path), monitor.console, autofix=monitor.autofix)
        mock_ty.assert_called_once_with(str(file_path), monitor.console)


def test_on_created_prints(tmp_path):
    monitor = PyFileMonitor()
    file_path = tmp_path / "test.py"
    file_path.write_text("print('hi')")
    event = DummyEvent(str(file_path))
    with patch.object(monitor, "console") as mock_console:
        monitor.on_created(event)  # type: ignore
        # Check that a Panel with the correct text is printed
        found = False
        for call in mock_console.print.call_args_list:
            panel = call.args[0]
            if hasattr(panel, "renderable") and "Created:" in str(panel.renderable) and str(file_path) in str(panel.renderable):
                found = True
        assert found, "Expected Panel with 'Created:' and file path not found in console output"


def test_ignores_non_py_files(tmp_path):
    monitor = PyFileMonitor()
    file_path = tmp_path / "test.txt"
    file_path.write_text("not python")
    event = DummyEvent(str(file_path))
    with patch.object(monitor, "console") as mock_console:
        monitor.on_modified(event)  # type: ignore
        monitor.on_created(event)  # type: ignore
        # Should not print anything for non-py files
        assert not mock_console.print.called


def test_ruff_check_error_message(tmp_path):
    file_path = tmp_path / "bad.py"
    file_path.write_text("def f(:\n    pass")
    with patch("ruffit.utils.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = "E999 SyntaxError: invalid syntax"
        with patch("rich.console.Console") as mock_console_class:
            mock_console = mock_console_class.return_value
            utils.run_ruff_check(str(file_path), mock_console)
            found = False
            for call in mock_console.print.call_args_list:
                panel = call.args[0]
                if hasattr(panel, "renderable") and "ruff check issues for" in str(panel.renderable) and "E999 SyntaxError: invalid syntax" in str(panel.renderable):
                    found = True
            assert found, "Expected error message not found in console output"


def test_debounce_prevents_duplicate(tmp_path):
    monitor = PyFileMonitor()
    file_path = tmp_path / "debounce.py"
    file_path.write_text("print('debounce')")
    event = DummyEvent(str(file_path))
    with (
        patch("ruffit.utils.run_ruff_format"),
        patch("ruffit.utils.run_ruff_check"),
        patch("ruffit.utils.run_ty_check"),
        patch.object(monitor, "console") as mock_console,
    ):
        monitor.on_modified(event)  # type: ignore
        monitor.on_modified(event)  # type: ignore
        # Only one Panel with "Modified:" should be printed
        modified_calls = [
            call for call in mock_console.print.call_args_list
            if hasattr(call.args[0], "renderable") and "Modified:" in str(call.args[0].renderable)
        ]
        assert len(modified_calls) == 1
