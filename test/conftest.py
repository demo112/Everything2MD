import pytest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

# Add src to sys.path to support imports like 'from core.utils import ...'
# This assumes the test folder is at project_root/test
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session", autouse=True)
def mock_tkinter_session():
    """
    Mock tkinter globally for the entire test session.
    This prevents 'attribute name must be string' errors and ensures
    no GUI windows are opened during tests.
    """

    # Create a robust mock for variables
    def create_mock_var(value=None, *args, **kwargs):
        m = MagicMock()
        initial_value = value if value is not None else ""
        m.get.return_value = initial_value

        def set_val(val):
            m.get.return_value = val

        m.set.side_effect = set_val

        # Make sure str(var) or similar doesn't cause issues if used
        m.__str__.return_value = str(initial_value)
        return m

    # Create the main tkinter mock
    mock_tk = MagicMock()

    # Define mock classes for variable types to support isinstance checks
    class MockVar(MagicMock):
        def __init__(self, value=None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._value = value if value is not None else ""
            self.get = MagicMock(return_value=self._value)
            self.set = MagicMock(side_effect=self._set_value)
            # Make sure str(var) works
            self.__str__ = lambda x: str(self._value)

        def _set_value(self, val):
            self._value = val
            self.get.return_value = val

    class MockStringVar(MockVar): pass
    class MockBooleanVar(MockVar): pass
    class MockIntVar(MockVar): pass

    # Assign classes to the mock module
    mock_tk.StringVar = MockStringVar
    mock_tk.BooleanVar = MockBooleanVar
    mock_tk.IntVar = MockIntVar

    # Mock other submodules
    mock_ttk = MagicMock()
    mock_filedialog = MagicMock()
    mock_messagebox = MagicMock()

    # Patch sys.modules
    # We use patch.dict to ensure it's reversible if needed, but for session scope it persists
    with pytest.helpers.patch_sys_modules(
        {
            "tkinter": mock_tk,
            "tkinter.ttk": mock_ttk,
            "tkinter.filedialog": mock_filedialog,
            "tkinter.messagebox": mock_messagebox,
        }
    ):
        yield


# Helper to patch sys.modules cleanly
class Helpers:
    from unittest.mock import patch

    @staticmethod
    def patch_sys_modules(modules_dict):
        return Helpers.patch.dict(sys.modules, modules_dict)


@pytest.fixture(scope="session")
def helpers():
    return Helpers


def pytest_configure(config):
    config.addinivalue_line("markers", "helpers: helper functions")
    # Attach helpers to pytest namespace if needed, or just use class above
    pytest.helpers = Helpers
