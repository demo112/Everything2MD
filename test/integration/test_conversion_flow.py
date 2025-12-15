import pytest
import os
from pathlib import Path
from src.core.engine import ConversionEngine
from src.core.config import ConfigManager

@pytest.mark.integration
def test_full_conversion_flow(tmp_path):
    """
    Test the full flow from creating a file -> engine -> output
    Currently using .txt as it doesn't require external tools.
    """
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    
    # 1. Prepare Data
    src_file = input_dir / "sample.txt"
    src_file.write_text("# Hello World\nThis is a test.")
    
    # 2. Setup Engine
    config = ConfigManager(str(tmp_path / "config.json"))
    engine = ConversionEngine(config)
    
    # 3. Run
    engine.run(str(input_dir), str(output_dir))
    
    # 4. Verify
    expected_out = output_dir / "sample.md"
    assert expected_out.exists()
    assert expected_out.read_text() == "# Hello World\nThis is a test."

@pytest.mark.integration
def test_gui_integration():
    """Verify GUI can import core modules (Smoke Test)"""
    try:
        from src.gui.main import Everything2MDGUI
        import tkinter as tk
        root = tk.Tk()
        app = Everything2MDGUI(root)
        root.destroy()
    except Exception as e:
        pytest.fail(f"GUI failed to initialize: {e}")
