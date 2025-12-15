import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys

# Mock tkinter before importing gui.main
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()

import tkinter as tk
from src.gui.main import Everything2MDGUI

@pytest.fixture
def mock_root():
    return MagicMock()

def test_gui_initialization(mock_root):
    """Test that GUI initializes and loads default config"""
    # Mock load_config to avoid file I/O during init if needed, 
    # but we might want to test it.
    
    with patch('src.gui.main.Everything2MDGUI.load_config') as mock_load:
        app = Everything2MDGUI(mock_root)
        
        # Check if variables are initialized (they are tk.StringVar which are mocked)
        # Since we mocked tkinter, tk.StringVar() returns a MagicMock
        assert app.root == mock_root
        mock_load.assert_called_once()

def test_load_config_defaults(mock_root):
    """Test loading config when file doesn't exist"""
    # We need to unmock load_config for this test, so we instantiate normally
    # But we need to mock json.load and open
    
    app = Everything2MDGUI(mock_root)
    
    # Setup the mock vars since they are MagicMocks from sys.modules['tkinter']
    # We need to ensure .set() works or verify it's called
    
    with patch("os.path.exists", return_value=False):
        app.load_config()
        
        # Verify defaults are set
        # Since tk.StringVar is mocked, we check if set() was called with defaults
        app.log_level.set.assert_any_call("INFO")
        app.output_format.set.assert_any_call("markdown")

def test_start_conversion_validation(mock_root):
    """Test validation before conversion"""
    app = Everything2MDGUI(mock_root)
    
    # Mock input path empty
    app.input_path.get.return_value = ""
    
    # Mock messagebox
    # Note: In main.py, it imports messagebox from tkinter
    # We mocked sys.modules['tkinter.messagebox'] but main.py does `from tkinter import messagebox`
    # So we should patch where it is used or patch tkinter.messagebox if imported that way.
    # main.py: `from tkinter import ttk, filedialog, messagebox`
    
    with patch('src.gui.main.messagebox.showerror') as mock_msg:
        app.start_conversion()
        mock_msg.assert_called_with("错误", "请选择输入路径")
        
    # Mock input path provided but output empty
    # Note: In start_conversion, it does:
    # if not self.input_path.get(): ...
    # if not self.output_path.get(): ...

    # We need to set input_path to something non-empty for the second call
        # Since app.input_path is a Mock, we can configure it
        app.input_path.get.return_value = "C:/test/input"
        app.output_path.get.return_value = ""

        # Re-patch messagebox to ensure we get a fresh mock if needed, or just assert on the same one
        # The previous block used `with patch...` so mock_msg is closed. We open a new one.
        # Note: app.input_path.get is called multiple times.
        # 1. start_conversion -> if not self.input_path.get()
        # 2. start_conversion -> if not self.output_path.get()
        
        # When we set return_value, it's fixed.
        # But wait, `test_start_conversion_validation` is failing with "Actual: showerror('错误', '请选择输入路径')"
        # This means `if not self.input_path.get()` evaluated to True (path is empty).
        # But we set `app.input_path.get.return_value = "C:/test/input"`.
        # Why?
        
        # app.input_path is a MagicMock created by sys.modules['tkinter'].StringVar()
        # In test_gui_initialization, we saw it's a MagicMock.
        # Maybe we are not setting it on the same instance?
        # app.input_path is created in __init__.
        
        # Let's try side_effect to debug or verify.
        # Actually, maybe the first test block "polluted" the mock if we reused the app instance?
        # No, we created app once.
        
        # Ah, in the first block:
        # app.input_path.get.return_value = ""
        # app.start_conversion() -> input check fails -> returns.
        
        # In the second block:
        # app.input_path.get.return_value = "C:/test/input"
        # app.start_conversion() -> input check passes -> output check fails.
        
        # Why did it fail? "Actual: showerror('错误', '请选择输入路径')"
        # This implies input check failed.
        # Maybe `app.input_path` was replaced or something? No.
        
        # Is it possible that `get()` is not called?
        # Tkinter StringVar get() returns string.
        
        # Wait, `app.input_path` is a property or attribute?
        # `self.input_path = tk.StringVar()`
        
        # Let's verify if return_value setter works on MagicMock.
        # It should.
        
        # Maybe we need to reset the mock?
        # app.input_path.get.reset_mock()
        
        # Or maybe the assertion failure is confusing.
        # "Expected: showerror('错误', '请选择输出路径')"
        # "Actual: showerror('错误', '请选择输入路径')"
        # This confirms input check failed.
        
        # Let's try creating a new app instance for the second test case to be safe.
        
    def test_start_conversion_validation_output(mock_root):
        app = Everything2MDGUI(mock_root)
        app.input_path.get.return_value = "C:/test/input"
        app.output_path.get.return_value = ""
        
        with patch('src.gui.main.messagebox.showerror') as mock_msg:
            app.start_conversion()
            mock_msg.assert_called_with("错误", "请选择输出路径")

