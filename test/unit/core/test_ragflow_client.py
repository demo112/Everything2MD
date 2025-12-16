import pytest
import json
import httpx
from unittest.mock import Mock, patch
from src.core.ragflow_client import RAGFlowClient

@pytest.fixture
def client():
    return RAGFlowClient("http://mock-api", "mock-key")

def test_list_datasets(client):
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.json.return_value = {"code": 0, "data": [{"id": "1", "name": "test"}]}
        mock_instance.get.return_value = mock_resp
        
        data = client.list_datasets()
        assert len(data) == 1
        assert data[0]["name"] == "test"
        
        mock_instance.get.assert_called_once()

def test_create_dataset(client):
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.json.return_value = {"code": 0, "data": {"id": "kb1", "name": "new_kb"}}
        mock_instance.post.return_value = mock_resp
        
        data = client.create_dataset("new_kb")
        assert data["id"] == "kb1"
        assert data["name"] == "new_kb"

def test_create_dataset_with_template(client):
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.json.return_value = {"code": 0, "data": {"id": "kb1", "name": "new_kb"}}
        mock_instance.post.return_value = mock_resp
        
        # Should just log info and proceed
        data = client.create_dataset("new_kb", template_id="tpl1")
        assert data["id"] == "kb1"

def test_upload_document(client, tmp_path):
    # Create dummy file
    f = tmp_path / "test.md"
    f.write_text("content")
    
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.json.return_value = {"code": 0, "data": {"id": "doc1"}}
        mock_instance.post.return_value = mock_resp
        
        res = client.upload_document("kb1", str(f))
        assert res["id"] == "doc1"

def test_upload_missing_file(client):
    with pytest.raises(FileNotFoundError):
        client.upload_document("kb1", "nonexistent.md")

def test_list_documents(client):
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.json.return_value = {"code": 0, "data": [{"id": "doc1"}]}
        mock_instance.get.return_value = mock_resp
        
        data = client.list_documents("kb1", keywords="test")
        assert len(data) == 1
        assert data[0]["id"] == "doc1"

def test_run_parsing(client):
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.json.return_value = {"code": 0, "data": None}
        mock_instance.post.return_value = mock_resp
        
        res = client.run_parsing("kb1", ["doc1", "doc2"])
        assert res is None

def test_api_error(client):
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.json.return_value = {"code": 1, "message": "fail"}
        mock_resp.raise_for_status = Mock()
        mock_instance.get.return_value = mock_resp
        
        with pytest.raises(Exception, match="API Error.*fail"):
            client.list_datasets()

def test_api_error_includes_url(client):
    """Test that API errors include the URL for debugging"""
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.json.return_value = {"code": 1, "message": "something wrong"}
        mock_resp.raise_for_status = Mock()
        mock_instance.get.return_value = mock_resp
        
        # We expect the URL to be in the error message
        with pytest.raises(Exception) as excinfo:
            client.list_datasets()
        
        error_msg = str(excinfo.value)
        assert "API Error" in error_msg
        assert "something wrong" in error_msg
        assert "http://mock-api/api/v1/datasets" in error_msg

def test_http_error(client):
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        # Mock raise_for_status to raise HTTPStatusError
        error = httpx.HTTPStatusError("500 Error", request=Mock(), response=mock_resp)
        mock_resp.raise_for_status.side_effect = error
        
        mock_instance.get.return_value = mock_resp
        
        with pytest.raises(Exception, match="HTTP Error 500"):
            client.list_datasets()

def test_json_decode_error(client):
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_resp = Mock()
        mock_resp.raise_for_status = Mock()
        mock_resp.json.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)
        mock_resp.text = "Not JSON"
        mock_instance.get.return_value = mock_resp
        
        with pytest.raises(Exception, match="Invalid JSON response"):
            client.list_datasets()

def test_unknown_error(client):
    with patch("httpx.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.__enter__.return_value = mock_instance
        
        mock_instance.get.side_effect = Exception("Network Error")
        
        with pytest.raises(Exception):
            client.list_datasets()
