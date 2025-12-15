import sys
import os
import pytest
import shutil
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "web" / "backend"))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

@pytest.fixture
def mock_config():
    """Mock ConfigManager"""
    from core.config import ConfigManager
    config = MagicMock(spec=ConfigManager)
    config.get.side_effect = lambda k, d=None: d
    return config

@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temp workspace with input/output dirs"""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    return input_dir, output_dir

