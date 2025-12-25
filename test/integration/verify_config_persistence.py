import sys
import os
import unittest
import tkinter as tk
from pathlib import Path
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from core.config import ConfigManager
from gui.main import Everything2MDGUI

class TestConfigPersistence(unittest.TestCase):
    def setUp(self):
        # Create a temp directory for config
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "config.json")
        
        # Initialize Tk root
        self.root = tk.Tk()
        self.root.withdraw() # Hide window
        
    def tearDown(self):
        self.root.destroy()
        shutil.rmtree(self.test_dir)

    def test_config_manager_mapping(self):
        """Test if ConfigManager uses mapping correctly without if/else logic"""
        cm = ConfigManager(self.config_path)
        
        # Test setting a new structured cleaning config
        cm.set("struct_clean_enabled", True)
        cm.set("struct_clean_api_key", "sk-test-123")
        
        # Reload
        cm2 = ConfigManager(self.config_path)
        self.assertTrue(cm2.get("struct_clean_enabled"))
        self.assertEqual(cm2.get("struct_clean_api_key"), "sk-test-123")

    def test_gui_binding(self):
        """Test if GUI binds variables correctly and saves them"""
        # patch ConfigManager to use our temp path
        # We can pass it to GUI if constructor allowed, but GUI inits its own.
        # So we need to patch the ConfigManager class used by GUI or modify GUI to accept it.
        # Looking at GUI code: self.config_manager = ConfigManager() (line 65)
        # It doesn't take args. But ConfigManager __init__ takes config_path.
        
        # Let's monkeypatch ConfigManager in gui.main
        import gui.main
        original_cm = gui.main.ConfigManager
        
        # Create a factory that returns our CM
        def mock_cm_factory():
            return ConfigManager(self.config_path)
            
        gui.main.ConfigManager = mock_cm_factory
        
        try:
            app = Everything2MDGUI(self.root)
            
            # 1. Verify initial load (should be default)
            self.assertFalse(app.struct_clean_enabled.get())
            
            # 2. Modify GUI variables
            app.struct_clean_enabled.set(True)
            app.struct_clean_api_key.set("gui-test-key")
            app.log_level.set("DEBUG")
            
            # 3. Save
            app.save_config(show_dialog=False)
            
            # 4. Verify file content
            cm = ConfigManager(self.config_path)
            self.assertTrue(cm.get("struct_clean_enabled"))
            self.assertEqual(cm.get("struct_clean_api_key"), "gui-test-key")
            self.assertEqual(cm.get("log_level"), "DEBUG")
            
            # 5. Reload GUI to verify load_config
            app.struct_clean_enabled.set(False) # Reset
            app.load_config()
            self.assertTrue(app.struct_clean_enabled.get())
            
        finally:
            gui.main.ConfigManager = original_cm

if __name__ == '__main__':
    unittest.main()
