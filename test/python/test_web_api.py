import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open, MagicMock
import json
from pathlib import Path

# Import app. Since we added web/backend to sys.path, we might import it as 'main'
# But to be safe and avoid conflict with gui/main.py, we should rely on PROJECT_ROOT being in path
from web.backend.main import app

client = TestClient(app)

def test_read_config_default():
    """Test getting config when file does not exist (default values)"""
    with patch("pathlib.Path.exists", return_value=False):
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "conversion_settings" in data
        assert data["conversion_settings"]["log_level"] == "INFO"
        assert data["conversion_settings"]["output_format"] == "markdown"

def test_read_config_existing():
    """Test getting config when file exists"""
    mock_config = {
        "conversion_settings": {
            "log_level": "DEBUG",
            "output_format": "html",
            "batch_processing": {
                "enabled": "false",
                "max_parallel_jobs": "4",
                "file_filters": ["pdf"]
            }
        }
    }
    
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
        
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert data["conversion_settings"]["log_level"] == "DEBUG"

def test_save_config():
    """Test saving configuration"""
    new_config = {
        "conversion_settings": {
            "log_level": "WARNING",
            "output_format": "txt",
            "batch_processing": {
                "enabled": "true",
                "max_parallel_jobs": "1",
                "file_filters": ["docx"]
            }
        }
    }
    
    with patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("builtins.open", mock_open()) as mock_file:
        
        response = client.post("/api/config", json=new_config)
        assert response.status_code == 200
        
        # Verify mkdir called
        mock_mkdir.assert_called()
        
        # Verify file write
        handle = mock_file()
        handle.write.assert_called()
        
        # Check if written content contains our log level
        args, _ = handle.write.call_args
        written_data = args[0]
        assert "WARNING" in written_data

def test_websocket_connect():
    """Test WebSocket connection"""
    with client.websocket_connect("/ws/logs") as websocket:
        # Just connecting should be fine
        assert websocket
        # We can try to receive, but we might timeout if nothing is sent.
        # The backend sends nothing on connect.
        pass
