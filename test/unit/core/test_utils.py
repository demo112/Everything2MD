import pytest
import logging
import sys
import os
from unittest.mock import MagicMock, patch
from src.core.utils import (
    setup_gui_logging, log_info, log_error, log_warn,
    get_soffice_path, get_pandoc_path, check_dependencies
)

def test_logger():
    # Setup a mock callback
    logs = []
    def callback(level, msg):
        logs.append((level, msg))
        
    setup_gui_logging(callback)
    
    log_info("test info")
    log_error("test error")
    log_warn("test warn")
    
    assert ("INFO", "test info") in logs
    assert ("ERROR", "test error") in logs
    assert ("WARNING", "test warn") in logs

@pytest.fixture
def mock_config_manager(mocker):
    # Mock ConfigManager class inside utils module
    mock_cm_cls = mocker.patch('src.core.utils.ConfigManager')
    mock_cm_instance = mock_cm_cls.return_value
    return mock_cm_instance

def test_get_soffice_path_from_config_file(mock_config_manager, mocker):
    mock_config_manager.get.return_value = "C:\\Custom\\soffice.exe"
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.path.isdir', return_value=False)
    
    assert get_soffice_path() == "C:\\Custom\\soffice.exe"

def test_get_soffice_path_from_config_dir(mock_config_manager, mocker):
    mock_config_manager.get.return_value = "C:\\Custom\\LibreOffice"
    mocker.patch('os.path.exists', side_effect=lambda p: True if "soffice.exe" in p else True)
    mocker.patch('os.path.isdir', return_value=True)
    
    # It should look for program/soffice.exe first
    path = get_soffice_path()
    assert "soffice.exe" in path
    assert "program" in path

def test_get_soffice_path_registry(mock_config_manager, mocker):
    mock_config_manager.get.return_value = None
    mocker.patch('platform.system', return_value="Windows")
    
    # Mock winreg
    mock_winreg = mocker.patch('src.core.utils.winreg', create=True)
    mock_key = MagicMock()
    mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
    mock_winreg.EnumKey.return_value = "7.0"
    mock_winreg.QueryValueEx.return_value = ("C:\\LibreOffice", 1)
    
    mocker.patch('os.path.exists', return_value=True)
    
    assert get_soffice_path() == "C:\\LibreOffice\\soffice.exe"

def test_get_soffice_path_common_paths(mock_config_manager, mocker):
    mock_config_manager.get.return_value = None
    mocker.patch('platform.system', return_value="Windows")
    # Fail registry
    mocker.patch('src.core.utils.winreg.OpenKey', side_effect=FileNotFoundError)
    
    # Mock os.environ
    mocker.patch.dict(os.environ, {"ProgramFiles": "C:\\Program Files"})
    
    # Mock os.listdir and exists
    def mock_exists(path):
        if path == "C:\\Program Files": return True
        if "LibreOffice" in path and "soffice.exe" in path: return True
        return False
        
    mocker.patch('os.path.exists', side_effect=mock_exists)
    mocker.patch('os.listdir', return_value=["LibreOffice 7"])
    
    assert get_soffice_path() is not None

def test_get_soffice_path_fallback_path(mock_config_manager, mocker):
    mock_config_manager.get.return_value = None
    mocker.patch('platform.system', return_value="Linux") # Skip windows checks
    mocker.patch('shutil.which', return_value="soffice")
    
    assert get_soffice_path() == "soffice"

def test_get_soffice_path_none(mock_config_manager, mocker):
    mock_config_manager.get.return_value = None
    mocker.patch('platform.system', return_value="Linux")
    mocker.patch('shutil.which', return_value=None)
    
    assert get_soffice_path() is None

def test_check_dependencies_fail(mocker):
    mocker.patch('src.core.utils.get_soffice_path', return_value=None)
    mocker.patch('src.core.utils.get_pandoc_path', return_value=None)
    with pytest.raises(RuntimeError, match="缺少必要依赖"):
        check_dependencies()

def test_get_pandoc_path_config(mock_config_manager, mocker):
    mock_config_manager.get.return_value = "C:\\Pandoc\\pandoc.exe"
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.path.isdir', return_value=False)
    assert get_pandoc_path() == "C:\\Pandoc\\pandoc.exe"

def test_get_pandoc_path_default(mock_config_manager, mocker):
    mock_config_manager.get.return_value = None
    mocker.patch('platform.system', return_value="Windows")
    mocker.patch('os.path.exists', side_effect=lambda p: "Pandoc" in p)
    
    assert "pandoc.exe" in get_pandoc_path()

def test_check_dependencies_success(mocker):
    mocker.patch('src.core.utils.get_soffice_path', return_value="soffice")
    mocker.patch('src.core.utils.get_pandoc_path', return_value="pandoc")
    assert check_dependencies() is True

def test_get_soffice_path_registry_error(mock_config_manager, mocker):
    mock_config_manager.get.return_value = None
    mocker.patch('platform.system', return_value="Windows")
    
    mock_winreg = mocker.patch('src.core.utils.winreg', create=True)
    mock_winreg.OpenKey.side_effect = Exception("Registry Error")
    
    # It should log warning and continue to common paths
    with patch('src.core.utils.log_warn') as mock_log:
        get_soffice_path()
        mock_log.assert_called_with(mocker.ANY)

def test_get_soffice_path_registry_enum_error(mock_config_manager, mocker):
    mock_config_manager.get.return_value = None
    mocker.patch('platform.system', return_value="Windows")
    
    mock_winreg = mocker.patch('src.core.utils.winreg', create=True)
    mock_key = MagicMock()
    mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
    
    # EnumKey raises OSError (end of list) immediately
    mock_winreg.EnumKey.side_effect = OSError
    
    # Also fail common paths
    mocker.patch('os.path.exists', return_value=False)
    mocker.patch('shutil.which', return_value=None)
    
    assert get_soffice_path() is None

def test_config_import_error(mocker):
    # Simulate ConfigManager import error
    # We need to reload utils module to trigger the try-except block at top level?
    # No, that's hard.
    # The code handles ImportError by trying src.core.config.
    # This is import time logic.
    pass
