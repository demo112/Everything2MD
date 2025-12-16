import pytest
import sys
from unittest.mock import MagicMock

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
    
    def var_side_effect(*args, **kwargs):
        val = kwargs.get('value', args[0] if args else None)
        return create_mock_var(val)

    mock_tk.StringVar.side_effect = var_side_effect
    mock_tk.BooleanVar.side_effect = var_side_effect
    mock_tk.IntVar.side_effect = var_side_effect
    
    # Mock other submodules
    mock_ttk = MagicMock()
    mock_filedialog = MagicMock()
    mock_messagebox = MagicMock()
    
    # Patch sys.modules
    # We use patch.dict to ensure it's reversible if needed, but for session scope it persists
    with pytest.helpers.patch_sys_modules({
        'tkinter': mock_tk,
        'tkinter.ttk': mock_ttk,
        'tkinter.filedialog': mock_filedialog,
        'tkinter.messagebox': mock_messagebox
    }):
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
