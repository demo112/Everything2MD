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
    with patch('src.gui.main.messagebox.showwarning') as mock_msg:
        app.start_conversion()
        mock_msg.assert_called_with("警告", "请选择输入文件或目录")
        
    # Mock input path provided but output empty
    app.input_path.get.return_value = "C:/test/input"
    app.output_path.get.return_value = ""
    
    with patch('src.gui.main.messagebox.showwarning') as mock_msg:
        app.start_conversion()
        mock_msg.assert_called_with("警告", "请选择输出目录")

